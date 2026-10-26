#!/usr/bin/env bash
# =====================================================================
# Build anything in this repo.
#
#   scripts/build.sh master        every bullet, with IDs and tags, plus the
#                                  cover-letter skeleton and paragraph bank
#                                  -> build/master/
#   scripts/build.sh bases         one résumé and one letter per role type
#                                  (ds, mle, de, rs, uxr), with unverified
#                                  facts marked in orange -> build/bases/
#   scripts/build.sh cv            the academic CV -> build/cv.pdf
#   scripts/build.sh app applications/<folder> [--allow-unverified]
#                                  [--no-letter] [--jd FILE]
#   scripts/build.sh cv [--with-references]
#   scripts/build.sh bases --onepage      one-page build of every role type
#   One-page applications: put \def\OnePageFlag{1} in the application's app.tex.
#                                  -> applications/<folder>/out/
#                                  then runs preflight; exit 1 = don't send yet
#
# New application: scripts/new-application.sh <company-slug> [role-type] ["Role"]
# Needs XeLaTeX (MacTeX) and python3; `pip install pypdf` enables every check.
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")/.."
ENGINE="${ENGINE:-xelatex}"
TYPES="ds mle de rs uxr"

tex () {  # tex <outdir> <jobname> <tex code>
  # LaTeX works in a temp folder outside Dropbox (sync can lock its scratch
  # files); only the PDF and the log are copied into place.
  mkdir -p "$1"
  local tmp; tmp="$(mktemp -d "${TMPDIR:-/tmp}/cvbuild.XXXXXX")"
  if ! "$ENGINE" -interaction=nonstopmode -halt-on-error \
        -output-directory="$tmp" -jobname="$2" "$3" > "$tmp/console.txt" 2>&1; then
    echo "LaTeX failed for $1/$2. First error:"
    grep -n '^!' -A8 "$tmp/$2.log" | head -30 || tail -30 "$tmp/console.txt"
    cp "$tmp/$2.log" "$1/" 2>/dev/null || true
    rm -rf "$tmp"; exit 1
  fi
  cp "$tmp/$2.pdf" "$tmp/$2.log" "$1/"
  rm -rf "$tmp"
}

case "${1:-}" in
  master)
    tex build/master resume-master-catalog '\def\archetype{all}\input{resume.master.tex}'
    tex build/master cover-letter-master   '\def\archetype{all}\input{cover-letter.master.tex}'
    echo "Built build/master/resume-master-catalog.pdf and build/master/cover-letter-master.pdf"
    ;;

  bases)
    if [[ "${2:-}" == "--onepage" ]]; then
      for a in $TYPES; do
        tex build/bases "resume-$a-1p" "\def\OnePageFlag{1}\def\archetype{$a}\input{resume.master.tex}"
        python3 scripts/preflight.py --pdf "build/bases/resume-$a-1p.pdf" \
          --log "build/bases/resume-$a-1p.log" --kind resume --max-pages 1 --quiet || true
      done
      echo "Built build/bases/resume-<type>-1p.pdf (one-page builds)"
      exit 0
    fi
    for a in $TYPES; do
      tex build/bases "resume-$a"       "\def\archetype{$a}\input{resume.master.tex}"
      tex build/bases "cover-letter-$a" "\def\archetype{$a}\input{cover-letter.master.tex}"
      python3 scripts/preflight.py --pdf "build/bases/resume-$a.pdf" \
        --log "build/bases/resume-$a.log" --kind resume --quiet || true
    done
    echo "Built build/bases/ (orange '?' marks facts to verify in master/facts.tex)"
    ;;

  cv)
    if [[ "${2:-}" == "--with-references" ]]; then
      tex build cv-with-references '\def\WithReferences{1}\input{cv.tex}'
      echo "Built build/cv-with-references.pdf -- contains your referees' contact"
      echo "details. Send it to a person; do not commit it or put it on the web."
    else
      tex build cv '\input{cv.tex}'
      echo "Built build/cv.pdf (academic CV, no referee details)"
    fi
    ;;

  app)
    TARGET="${2:?usage: scripts/build.sh app applications/<folder> [--allow-unverified] [--no-letter] [--jd FILE]}"
    shift 2
    DIR="${TARGET%/}"; [[ "$DIR" == *.tex ]] && DIR="$(dirname "$DIR")"
    [[ -f "$DIR/app.tex" ]] || { echo "No $DIR/app.tex — start one with scripts/new-application.sh"; exit 1; }
    if [[ "$DIR" == *" "* ]]; then echo "Rename $DIR without spaces."; exit 1; fi
    JD=""; ALLOW=""; LETTER=1
    if [[ -f "$DIR/posting.txt" ]] && [[ $(wc -c < "$DIR/posting.txt") -gt 400 ]]; then JD="$DIR/posting.txt"; fi
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --jd) JD="$2"; shift 2 ;;
        --allow-unverified) ALLOW="--allow-unverified"; shift ;;
        --no-letter) LETTER=0; shift ;;
        *) echo "Unknown option $1"; exit 1 ;;
      esac
    done
    # Length is a property of the application: \def\OnePageFlag{1} in app.tex.
    MAXP=""
    if grep -qE '^[^%]*\\def\\OnePageFlag' "$DIR/app.tex"; then MAXP="--max-pages 1"; fi
    # The posting's own role title keeps its spelling ("Applied Researcher 2"),
    # so the number-style check is told to skip it.
    ROLE="$(sed -n 's/^[^%]*\\def\\Role{\(.*\)}.*$/\1/p' "$DIR/app.tex" | head -1)"
    VERB=""; [[ -n "$ROLE" ]] && VERB="--verbatim"
    NAME="$(basename "$DIR")"; OUT="$DIR/out"; mkdir -p "$OUT"
    : > "$OUT/preflight.txt"
    STATUS=0
    tex "$OUT" Carlos-Tejada-Resume "\def\FinalBuildFlag{1}\input{$DIR/app.tex}\input{resume.master.tex}"
    if ! python3 scripts/preflight.py --pdf "$OUT/Carlos-Tejada-Resume.pdf" --log "$OUT/Carlos-Tejada-Resume.log" \
      --kind resume --final $ALLOW $MAXP ${JD:+--jd "$JD"} ${VERB:+$VERB "$ROLE"} 2>&1 | tee -a "$OUT/preflight.txt"; then STATUS=1; fi
    if [[ $LETTER -eq 1 ]]; then
      tex "$OUT" Carlos-Tejada-Cover-Letter "\def\FinalBuildFlag{1}\input{$DIR/app.tex}\input{cover-letter.master.tex}"
      if ! python3 scripts/preflight.py --pdf "$OUT/Carlos-Tejada-Cover-Letter.pdf" --log "$OUT/Carlos-Tejada-Cover-Letter.log" \
        --kind letter --final $ALLOW ${VERB:+$VERB "$ROLE"} 2>&1 | tee -a "$OUT/preflight.txt"; then STATUS=1; fi
    fi
    { date +%F; git rev-parse --short HEAD 2>/dev/null || echo "(no commit)"; } > "$OUT/built-from.txt"
    echo
    if [[ $STATUS -eq 0 ]]; then
      echo "Ready: $OUT/"
      echo "When you send it:"
      echo "  git tag apply/$NAME        # records the master version you used"
      echo "  vault note: status Applied · date_applied $(date +%F) · resume_variant $NAME · channel cold|referral|recruiter"
    else
      echo "Not ready to send. Fix the items marked FAIL above, then rebuild."
    fi
    exit $STATUS
    ;;

  *)
    sed -n '3,20p' "$0"; exit 1 ;;
esac
