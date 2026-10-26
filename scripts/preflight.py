#!/usr/bin/env python3
"""Pre-send checks for PDFs built from the master résumé and cover letter.

    preflight.py --pdf FILE --kind resume|letter [--log FILE] [--final]
                 [--allow-unverified] [--jd POSTING.txt] [--max-pages N] [--quiet]

Exit code 1 means "don't send this yet". Works best with `pip install pypdf`;
falls back to poppler's pdftotext/pdfinfo if pypdf is missing.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

# Generic placeholders. Anything specific to Carlos -- an old phone number, the
# title of a paper under blind review -- goes in master/blocked.txt, which is
# untracked, because this repository is public.
PLACEHOLDERS = ["[[SLOT", "HANDLE", "Lorem ipsum", "Job Title", "Company's Address",
                "[paper title]", "Company Name", "Role title, exactly as posted"]

# Terms that postings ask for. Used only to REPORT coverage: add a term to the
# master only if it's true and you can discuss it in an interview.
LEXICON = {
    "Python": r"\bpython\b", "SQL": r"\bsql\b", "R": r"(?<![\w/])R(?![\w/+#-])",
    "statistics": r"statistic", "A/B testing / experimentation": r"a/b|experiment",
    "causal inference": r"causal", "regression": r"regression", "forecasting / time series": r"forecast|time[- ]series",
    "machine learning": r"machine learning|\bml\b", "deep learning": r"deep learning|neural net",
    "NLP": r"\bnlp\b|natural language", "LLM / GenAI": r"\bllms?\b|large language|generative|genai",
    "RAG / retrieval": r"retrieval|\brag\b", "recommendation / ranking": r"recommend|ranking|personaliz",
    "fraud / risk": r"fraud|\brisk\b", "marketing / growth": r"marketing|attribution|growth|retention|churn",
    "product metrics": r"product metric|\bkpis?\b|north star|product sense",
    "dashboards / BI": r"tableau|looker|power ?bi|dashboard", "Snowflake / BigQuery / Redshift": r"snowflake|bigquery|redshift",
    "dbt": r"\bdbt\b", "Airflow / Dagster / Prefect": r"airflow|dagster|prefect", "Spark / Databricks": r"spark|databricks",
    "AWS": r"\baws\b", "GCP": r"\bgcp\b|google cloud", "Azure": r"azure", "Docker": r"docker", "Kubernetes": r"kubernetes|\bk8s\b",
    "PyTorch / TensorFlow": r"pytorch|tensorflow", "scikit-learn": r"scikit|sklearn", "pandas / NumPy": r"pandas|numpy",
    "stakeholders": r"stakeholder|cross-functional", "user research / usability": r"user research|usability|\bux\b",
    "qualitative methods": r"qualitative|interview|thematic", "survey": r"\bsurveys?\b", "accessibility": r"accessib",
    "Ph.D.": r"ph\.?\s?d",
}

class Report:
    def __init__(self, quiet=False):
        self.fails, self.warns, self.quiet = 0, 0, quiet
    def ok(self, msg):
        if not self.quiet:
            print(f"  ok    {msg}")
    def warn(self, msg):
        self.warns += 1
        print(f"  WARN  {msg}")
    def fail(self, msg):
        self.fails += 1
        print(f"  FAIL  {msg}")

def read_pdf(path):
    """Return (list of page texts, page width, page height, extractor name)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        box = reader.pages[0].mediabox
        return [p.extract_text() or "" for p in reader.pages], float(box.width), float(box.height), "pypdf"
    except ImportError:
        pass
    if shutil.which("pdftotext") and shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
        m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
        text = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True).stdout
        pages = [p for p in text.split("\f") if p.strip()]
        return pages, float(m.group(1)), float(m.group(2)), "pdftotext"
    print("  WARN  install pypdf (pip install pypdf) or poppler to check the PDF text")
    return None, None, None, None

def link_uris(path):
    """Every URI carried by a /Link annotation, or None if they can't be read."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        out = []
        for page in PdfReader(path).pages:
            for ann in page.get("/Annots") or []:
                o = ann.get_object()
                if o.get("/Subtype") == "/Link":
                    uri = (o.get("/A") or {}).get("/URI")
                    if uri:
                        out.append(str(uri))
        return out
    except Exception:
        return None


def local_blocklist():
    """Extra strings that must never appear in a built PDF.

    Kept in master/blocked.txt, which is not tracked: the strings themselves
    can be confidential (an anonymised paper title, a client name), so they
    don't belong in a public repository. One per line, # for comments.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "master", "blocked.txt")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--kind", choices=["resume", "letter"], required=True)
    ap.add_argument("--log")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--allow-unverified", action="store_true")
    ap.add_argument("--jd")
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--verbatim", action="append", default=[],
                    help="A string quoted from the posting (a role title such as\n                          'Applied Researcher 2'). Exempt from the number-style\n                          check: their spelling is theirs, not ours.")
    a = ap.parse_args()
    r = Report(a.quiet)
    print(f"Preflight: {a.pdf}")

    pages, w, h, extractor = read_pdf(a.pdf)
    if pages is not None:
        text = "\n".join(pages)
        # 1. Paper size and length
        if abs(w - 612) < 2 and abs(h - 792) < 2:
            r.ok("US Letter")
        else:
            r.fail(f"page size is {w:.0f} x {h:.0f} pt, not US Letter (612 x 792)")
        max_pages = a.max_pages or (1 if a.kind == "letter" else 2)
        if len(pages) <= max_pages:
            r.ok(f"{len(pages)} page(s)")
        else:
            r.fail(f"{len(pages)} pages (limit {max_pages})")
        # 2. Characters parsers choke on
        pua = sorted({c for c in text if 0xE000 <= ord(c) <= 0xF8FF})
        (r.fail if pua else r.ok)("icon/private-use characters: " + (" ".join(f"U+{ord(c):04X}" for c in pua) if pua else "none"))
        # 3. Placeholders left in
        found = [p for p in PLACEHOLDERS + local_blocklist() if p in text]
        (r.fail if found else r.ok)("placeholders: " + (", ".join(found) if found else "none"))
        # 4. Words run together (what pypdf-based screeners see)
        merged = [t for t in re.findall(r"\S+", text) if len(t) >= 26 and not re.search(r"[/@]|\.com|https?", t)]
        (r.warn if merged else r.ok)(f"run-together words ({extractor}): " + (", ".join(merged[:3]) if merged else "none"))
        # 4b. Every visible link actually links, and to the right place.
        #     \XeTeXinterwordspaceshaping=2 silently merges consecutive \href
        #     annotations: one hotspot swallowed the whole contact line and sent
        #     GitHub, the website and Scholar to LinkedIn. \slink (an \mbox
        #     around the \href) is the fix; this is the alarm.
        uris = link_uris(a.pdf)
        if uris is not None:
            visible = set(re.findall(r"\b[\w.-]+\.(?:com|org|net|io|dev|edu|ai)(?:/[\w./~%#?=&-]*)?", text))
            visible |= set(re.findall(r"\b[\w.+-]+@[\w.-]+\.\w+\b", text))
            blob = " ".join(uris).lower()
            dead = sorted(v for v in visible if v.lower().rstrip("/.,;") not in blob)
            (r.warn if dead else r.ok)(
                "visible links are clickable: "
                + (", ".join(dead[:4]) + " not linked" if dead
                   else "%d link(s), all resolve" % len(uris)))

        # 5. Number style: spell out one through ten, numerals from 11 up.
        #    Exempt: percentages, currency, years, decimals, ranges, anything
        #    glued to a letter (F1, 3D, C8), page counts and requisition IDs.
        prose = text
        for v in a.verbatim:                                 # posting's own wording
            prose = prose.replace(v, " ")
        prose = re.sub(r"\b(19|20)\d\d\b", " ", prose)         # years
        prose = re.sub(r"\$\s?\d[\d,.]*", " ", prose)            # currency
        prose = re.sub(r"\d[\d,.]*\s?%", " ", prose)             # percentages
        prose = re.sub(r"\d+\.\d+", " ", prose)                 # decimals
        prose = re.sub(r"\d[\d,]{3,}", " ", prose)               # 4+ digit counts, IDs
        prose = re.sub(r"\d+\s?(?:--|–|-)\s?\d+", " ", prose)    # ranges
        prose = re.sub(r"\d+\s+pages?\b", " ", prose)           # citation page counts
        digits = re.findall(r"(?<![\w$.,-])(10|[1-9])(?![\w%.,-])", prose)
        if a.kind in ("resume", "letter"):
            (r.warn if digits else r.ok)(
                "number style (spell out 1-10): "
                + (", ".join(sorted(set(digits))) + " written as digits" if digits else "ok"))

        # 5. Letter length
        if a.kind == "letter":
            m = re.search(r"Dear(.*?)(Sincerely|Best regards|Kind regards)", text, re.S)
            if m:
                words = len(re.findall(r"[A-Za-z0-9][\w'’.-]*", m.group(1)))
                if 230 <= words <= 380:
                    r.ok(f"letter body: {words} words (target 250-350)")
                else:
                    r.warn(f"letter body: {words} words (target 250-350)")
            else:
                r.warn("couldn't find the salutation/sign-off to count words")

    # 6. Build log: unverified facts and unfilled slots
    if a.log:
        try:
            log = open(a.log, encoding="utf-8", errors="replace").read()
        except FileNotFoundError:
            log = ""
            r.warn(f"no log at {a.log}")
        unverified = sorted(set(re.findall(r"UNVERIFIED FACT: (.*)", log)))
        slots = sorted(set(re.findall(r"UNFILLED SLOT: (.*)", log)))
        if unverified:
            msg = f"{len(unverified)} unverified fact(s) in master/facts.tex:"
            if a.final and not a.allow_unverified:
                r.fail(msg)
            else:
                r.warn(msg)
            for u in unverified:
                print(f"          - {u.strip()[:90]}")
        else:
            r.ok("no unverified facts")
        if slots:
            msg = f"{len(slots)} unfilled slot(s): " + "; ".join(s.strip()[:50] for s in slots[:6])
            (r.fail if a.final else r.warn)(msg)
        elif a.kind == "letter":
            r.ok("all slots filled")

    # 7. Posting coverage report (never fails; honesty over keyword matching)
    if a.jd and pages is not None:
        try:
            jd = open(a.jd, encoding="utf-8", errors="replace").read()
        except FileNotFoundError:
            jd = ""
            r.warn(f"no posting text at {a.jd}")
        if jd:
            print("  Posting coverage (terms the posting uses):")
            low = text.lower()
            for term, rx in LEXICON.items():
                flags = 0 if term == "R" else re.I
                if re.search(rx, jd, flags):
                    have = re.search(rx, text if term == "R" else low, flags)
                    print(f"        {'in résumé ' if have else 'MISSING   '} {term}")
            print("        (add a missing term only if it's true and you can discuss it)")

    verdict = "FAIL: fix before sending" if r.fails else ("ok with warnings" if r.warns else "ok")
    print(f"  => {verdict}\n")
    sys.exit(1 if r.fails else 0)

if __name__ == "__main__":
    main()
