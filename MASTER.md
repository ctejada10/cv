# Master résumé and cover letter — working guide

One source for every application. You never rewrite a résumé per company: you
pick a role type, choose and order bullets from the master, write two short
custom pieces in the letter, and build. Facts live in one file, so every version
you send agrees with every other one — and with your LinkedIn and your CV.

## 1. The repository

| Path | What it is |
|---|---|
| `resume.master.tex` | Every accomplishment, once per phrasing, tagged by role type. Also the headline, summary, skills, publications, service and education blocks for each type. At the bottom: retired claims, and why each was dropped. |
| `cover-letter.master.tex` | The five-block letter, a bank of proof paragraphs, transitions and closes. |
| `master/facts.tex` | The single source of truth. `\unverified[label]{value}` marks what still needs checking. |
| `master/preamble.tex` | Layout and machinery. You shouldn't need to touch it. |
| `applications/<date>-<company>-<type>/` | One folder per application: `app.tex`, `posting.txt`, `out/`. Git-ignored. |
| `applications/_TEMPLATE/` | What `new-application.sh` copies. |
| `applications/_EXAMPLE-ds/` | A complete, fictional application ("Example Health"). Local only — not tracked. |
| `scripts/new-application.sh` | Starts an application folder. |
| `scripts/build.sh` | Builds the catalog, the bases, the CV, or one application. |
| `scripts/preflight.py` | The pre-send checks. |
| `build/` | Catalog, role-type bases, academic CV. Git-ignored. |

## 2. First time: settle the facts (about 45 minutes)

Run `scripts/build.sh bases` and open `build/bases/resume-ds.pdf`. Every orange
value with a `?` comes from `master/facts.tex` and needs checking against a
primary record: an offer letter, a contract, your appointment letter, LinkedIn.
When a value is right, delete the `\unverified[...]{ }` wrapper and keep the
value. Application builds refuse to finish while any remain (`--allow-unverified`
overrides it, but don't send that way).

| Flag | What to check |
|---|---|
| city | Where you live. Write "New York, NY" only if that's true. |
| LinkedIn handle | Your URL, in both places on that line. Then make LinkedIn's titles and dates match this file. |
| UW official title | Your appointment letter. UW usually says "Postdoctoral Scholar"; the academic CV says "Fellow". Dates confirmed 2025 – Present. |
| Aarhus official title | Your contract. Dates confirmed 2023 – 2024. |
| RIT dates | The CV lists Graduate Research Assistant 2014–2016 and Ph.D. Fellow at RIT 2017–2018; the résumés merged them into 2014–2018. |
| B.Sc. year | 2012 (CV) or 2013 (résumés). |
| UW mentees, UW team size | Current counts. |
| CHI paper title | For the publication lists. |

Two catalog-only flags block nothing: `uw-rag-eval` (add how you evaluated the
LLM descriptions — that's what makes LLM work credible) and `nc-sparktuning` (a
claim from one old variant).

Two errors to fix in `cv/publications.tex`: LaCir is CHI 2024, not 2021, and
MorpheesPlug reuses AirTouch's DOI.

## 3. Role types

| Type | For | Leads with | Letter defaults |
|---|---|---|---|
| `ds` | Data Scientist (ML, research-leaning, health, public sector) | LLM retrieval work, the 12-participant study and its log analysis, Netcompany pipeline and classifier | proof-nc-nlp, proof-uw-study |
| `mle` | ML / AI Engineer | the UW system and LLM companion, both Aarhus LLM tools, the classifier in production | proof-nc-nlp, proof-uw-rag |
| `de` | Data Engineer | Netcompany pipeline, tooling, access control; Tous portal and integrations | proof-nc-pipeline, proof-nc-tools |
| `rs` | Research Scientist (HCI, accessibility, human-centered AI) | UW system, study and co-design; full publications; service | proof-uw-system, proof-phd-experiments |
| `uxr` | Quantitative / mixed-methods UX Researcher | the study, co-design, study tooling, workshops; experiments | proof-uw-study, proof-uw-system |

Each base is two Letter pages (580–910 words). `rs` is longest because it carries
the full publication list.

## 4. One application, start to finish (20–30 minutes)

```sh
scripts/new-application.sh ramp ds "Senior Data Scientist, Growth"
```

1. Paste the posting into `applications/2026-09-15-ramp-ds/posting.txt`.
2. Open `app.tex`. Set the role type if it isn't right. Read the posting and pick
   bullets: `\ExcludeIDs` drops one, `\IncludeIDs` pulls one in from another role
   type. IDs are in `build/master/resume-master-catalog.pdf`.
3. Optional: `\HeadlineOverride`, `\SummaryOverride`, `\SkillsOverride`, or a
   one-off rewording of a single bullet with
   `\expandafter\def\csname override@<id>\endcsname{...}`. Same facts, new emphasis.
4. Write the two custom pieces of the letter — the hook and "why them" — and pick
   the two proof paragraphs. Or add `--no-letter`.
5. `scripts/build.sh app applications/2026-09-15-ramp-ds`
   The PDFs, the preflight report and the master commit land in `out/`. The
   posting is used for a coverage report: which of its terms your résumé uses.
   Add a missing term only if it's true and you can discuss it in an interview.
6. Send, ideally through the company's own ATS and within a few days of the
   posting appearing. Then `git tag apply/2026-09-15-ramp-ds`, and record in the
   vault note: `status`, `date_applied`, `resume_variant` (the folder name) and
   `channel` (cold, referral, recruiter).

Reapplying later, or a second role at the same company, means a new dated folder.
Nothing gets overwritten, and you can always see exactly what you sent.

## 4a. Two pages or one

Every application builds at two pages by default. For analyst and
product-analytics roles — and anywhere a two-page Ph.D. résumé would read as
overqualified — put this line in the application's `app.tex`:

```latex
\def\OnePageFlag{1}
```

The build then drops Tous, RIT and the research service block, keeps 2 bullets
at UW, 1 at Aarhus, 2 at Netcompany and 1 at the Ph.D., cuts publications to the
summary line, and tightens spacing: about 450 words instead of 900. Preflight
enforces the single page. `scripts/build.sh bases --onepage` shows all five role
types at that length.

It costs you the capstone and Bitey bullets, which go with RIT. When a posting
asks for evaluation rigour or signal processing, stay at two pages.

## 5. Why applications are folders (and what else was considered)

**What we do:** a settings file plus the posting plus the built PDFs, one folder
per application, git-ignored, with a git tag recording which master version it
came from. When a recruiter calls three weeks later, one folder holds the posting
you answered, the exact PDFs you sent, and the checks that passed.

Alternatives, and why not:

- **A branch per application.** Full freedom, real history — but you'd rebase
  every branch each time the master improves, and facts would drift again. The
  only real per-application deltas are *which* bullets and two paragraphs of
  prose; a 20-line settings file captures that exactly.
- **Copy the master and trim it.** This is how the 22 variants happened. Every
  copy is a fork of the facts; nothing propagates; contradictions accumulate.
- **A data-driven pipeline** (YAML/JSON plus a generator such as RenderCV or
  JSON Resume). Cleaner separation of content and layout, and it would give you
  plain-text and HTML versions for text boxes. It's also a rewrite, with less
  control over this layout. Worth revisiting if you start needing several output
  formats; the content already lives in one place, so a move would be mechanical.
- **An index file of applications in the repo.** Your Obsidian vault already
  tracks status, dates and outcomes, and two trackers always disagree. The repo
  keeps what was sent; the vault keeps what happened. `build.sh` prints the line
  to paste into the vault note.

**On measuring what works:** a few dozen applications can't tell one
résumé version from another — separating a 5% rate from a 10% rate takes hundreds
of applications. Log `resume_variant` and `channel` anyway, and compare only the
big contrast: referral versus cold.

## 6. Rules

- **Facts live in `master/facts.tex` only.** An application file chooses and
  orders. It never changes a title, date or number.
- **New accomplishment?** Add `\bul{new-id}{types}{text}` to the right role in
  `resume.master.tex`, rebuild the catalog, use it from then on.
- **Official titles, with a descriptor.** "IT Consultant (Data & ML)" — the
  title on the contract, plus what the work was. The line under your name is a
  field label, not a job title.
- **Say what the method was.** Describe each evaluation as what it was —
  parameter studies, held-out test sets, cross-validation, error analysis. Claim
  a method only where a paper or a record shows it: interviewers probe power,
  randomization units and diff-in-diff.
- **Skills you can defend.** The master keeps an "also on file" list in a comment
  (XGBoost, Kubernetes, AWS, Databricks…). Leave those off unless you can talk
  about them.
- **Numbers one through ten are words; 11 and up are numerals.** "four
  undergraduates", "an eight-person team", "six years of research" — but "12
  participants", "830 labeled samples". The counts live in `master/facts.tex`
  already spelled (`\FactUWTeam` is literally `eight`), so a new application
  inherits the rule without thinking about it. Exempt, as usual: percentages
  (87% F1), years, decimals (1.6 hours), ranges, page counts in citations, and
  anything glued to a letter (F1, 3D, C8). Also exempt is the posting's own role
  title — "Applied Researcher 2" keeps their spelling, and `build.sh` passes it
  to preflight with `--verbatim` so the check skips it.
- **The name line carries the doctorate; the headline does not repeat it.**
  `\FactPostNominal` holds `, Ph.D.` and the résumé and letter headers render it.
  The advice converges for a terminal degree in the field you're applying in:
  JobStars calls a doctorate after the name "absolutely appropriate, especially
  in fields where advanced academic or professional specialization is the norm",
  and the objections in the literature are all about MBA, PMP and BS — Kyla
  Duffy's 2021 rule that terminal degrees belong next to the name survived her
  own later revision that struck MBA and PMP off it. Because the credential is
  now on the name line, every headline dropped its trailing "Ph.D. in Computer
  Science" segment; carrying it twice in two lines reads as insecurity. One or
  the other, never both. The summaries dropped it too: with the name line
  carrying it, "Computer scientist (Ph.D.) specializing in..." was the third
  mention in four lines. Set `\FactPostNominal` to `{}` to go back, and put it
  back in the headline if you do. The academic
  CV keeps a plain name — the whole document is the credential — and so does the
  letter's signature block.
- **No hidden text, no keyword stuffing.** Parsing strips formatting, so
  reviewers see it.
- The bottom of `resume.master.tex` lists the **retired claims** and why each was
  dropped. Don't bring one back without new evidence.

- **The under-review paper carries authorship, not subject.** List it as
  *Under review: Lead author on a multidisciplinary submission to <venue>. Title
  and details withheld during double-blind review.* Double-blind rules do not
  require this — ICSME's FAQ says plainly that reviewing "should not hinder the
  usual communication of results", and authors may list and even post work under
  review. The redaction is Carlos's own caution, and the cost of it is that the
  entry says nothing about what the work is. Authorship position is the part a
  hiring committee reads anyway, so lead that with it. Status must always be
  marked (UCLA's CV guide: "Publication status should be clearly marked").
  `\FactUWPaperDesc` holds this string; nothing else may describe the paper.
- **The M.Sc. capstone stays off the résumé.** It is from 2016 and reads as
  student work next to a Ph.D. and two postdocs. The cross-validation leakage
  story it contains is still the best evidence of evaluation judgment Carlos
  has, so it lives in the cover-letter bank as `proof-capstone-leak` and in the
  Skills line as "leakage detection" — use it as an interview answer, not as
  résumé real estate. If a posting makes it the single best proof available,
  tell it for the lesson, never as a project.

## 7. The cover letter

Five blocks, 250–350 words, one page. The hook and the "why them" are written
fresh every time; everything between them is selected from the bank in
`cover-letter.master.tex`.

**The rule that matters most: the letter must carry what the résumé cannot.**
The résumé already says what you built and what it scored. The letter says what
the decision was, what surprised you, what broke, what you enjoyed. A paragraph
that restates a bullet in longer sentences is wasted paper — Alison Green's test
is whether the letter is just "your résumé in different words." The rewrite she
holds up as working turns on one small, concrete, slightly odd fact: *"I probably
was the first to read the entire manual, which made me 'the P560 person'."*
Nobody else could write that sentence. That is the whole trick.

| Block | Words | What it is |
|---|---|---|
| Hook | 45–65 | The one true sentence about why this posting and not another |
| Proof 1 | 70–90 | A bank paragraph + one sentence carrying the judgement inside the work |
| Proof 2 | 60–80 | A second bank paragraph + a transition |
| Why them | 40–60 | Where you have actually touched their work, and what you'd start on |
| Close | 20–35 | From the bank |

**A letter that never mentions the job is the opposite failure.** Avoiding the
posting's language is not the same as avoiding its content, and the first fix
overshot into a letter that listed three things Carlos had built and left the
reader to draw the conclusion. His verdict: *"it's just listing things I did. It
needs to relate to the post and convince them that I am a good candidate to
interview and hire."* The letter is an argument, and an argument needs both
halves.

- **Banned** is echoing a requirement back as a claim: *You need someone with
  strong ML skills, and I have strong ML skills.* That is their sentence with
  his name in it, and it carries no information.
- **Required** is showing you understand the problem behind the requirement, and
  putting your evidence against it. The Code|AI posting says "from using RAG to
  evaluation" and "taking these from research into product." So the letter
  claims retrieval and evaluation rarely live in one person, proves both, and
  uses Netcompany — prototype to deployed government system, held through drift
  — as the research-into-product evidence. None of their phrasing is repeated;
  every paragraph answers something they asked for.
- **Read the preferred qualifications for the gap, and answer it in the letter.**
  Carlos has no CodeLLM or AI-IDE experience. Rather than hide that or apologise
  for it, the letter gives the nearest true thing — the Aarhus tool that turns a
  prompt into printable CAD and validates the geometry before it ships — as its
  own paragraph. A near-miss stated plainly reads as honesty; a gap left silent
  reads as a gap.
- **Make the bridge explicit.** His users are blind, theirs are developers. The
  hook does the work in one sentence: someone who cannot see an answer cannot
  catch that it is wrong, and *"a developer reading a suggestion is in a milder
  version of the same position."* Without that sentence the accessibility work
  looks like a different field.

**Block 4 is not a compliment.** It's the place where you have really touched
their work: a product you use, a paper you read, a tool you built on, a bug you
hit. "You ship at scale and still publish" could be pasted into any letter and
therefore says nothing. If you have no genuine point of contact, delete the
block — a shorter letter beats a flattering one.

**The rhythm is the tell.** Carlos rejected three drafts as "AI slop" and the
thing he was reacting to was never the facts — it was the shape of the sentences.
Every paragraph landed on a reversal: *The hard part was never the prompt. It was
X.* / *Launch was the easy part.* / *not whether they pressed Tab.* One of those
is a good sentence; four in a row is a machine performing insight. Rules that
came out of it:

- **One turn per letter, at most.** If two paragraphs both end on a
  short reversing sentence, cut one back to a plain statement of fact.
- **Don't announce your own thesis.** "I spend my time on two things:" and
  "I build X and then find out whether it works" are setups, not content, and
  the second reads as though he ships without checking. Say the thing.
- **No reaching for a connection.** "So I've been on the user end of what you
  ship" (because his code is on GitHub, and GitHub is Microsoft) is the sort of
  stretch that reads as trying too hard. Block 4 needs a real point of contact
  or nothing.
- **End on a fact, not a flourish.** "I would not run a study on either alone
  now" beats "the gap is usually the finding."

**Banned everywhere**, because these are exactly what generated letters do:
restating the posting back at them; praise that would fit any employer; claiming
you exceed the requirements; a paragraph-closing aphorism and the em-dash pivot
that sets it up; "I am writing to express my interest"; weak verbs (*helped
with*, *assisted*); and announcing what you don't have.

**Why specificity is the whole strategy.** Since generative writing tools
arrived, letters that echo a posting's keywords stopped predicting callbacks
(Cui, Dias & Ye 2025; Galdin & Silbert 2025), and Harvard's 2026 guidance warns
that recruiters now recognise unedited AI by its generic, over-formal register.
The only thing left that carries information is detail that had to come from you.

- Every visible URL is clickable and points where it reads. `\XeTeXinterword-
  spaceshaping=2` — the setting that stops parsers reading "Datascientistwith" —
  silently merges consecutive `\href` annotations: the first link's hotspot
  stretches across the whole line and the rest get no annotation at all. The
  whole contact line pointed at LinkedIn for who knows how long. Use `\slink`
  (an `\mbox` around the `\href`) for any link sharing a line with another.

## 8. What preflight checks

- US Letter; résumé 2 pages at most, letter 1 page.
- No icon characters; words come out separated (what pypdf-based screeners read).
- No placeholders: `HANDLE`, `[[SLOT`, "Lorem", "Job Title", and anything
  listed in `master/blocked.txt`.
- Unverified facts and unfilled slots, from the build log.
- Letter length (warns outside 230–380 words).
- With a posting: which of its terms the résumé covers.

Once, by hand: upload a PDF to open-resume.com/resume-parser, or start (without
submitting) a Greenhouse or Lever application with résumé autofill, and check the
parsed name, location, links and each job's title and dates.

## 9. Why it looks like this

The layout is the tested fix list from the Résumé Audit (vault: 30 Professional →
31 Career): Letter paper; ragged-right text with no hyphenation; real spaces in
the PDF text layer; titles and dates in regular dark type; a plain-text header
with visible URLs and no icons; no footer; standard section names; a role's
header never separated from its first bullet.

## 10. Privacy

This repository is public on GitHub, so the rule is simple: **the system is
tracked, the output is not.**

Tracked: `resume.master.tex`, `cover-letter.master.tex`, `master/`, `scripts/`,
`applications/_TEMPLATE/`, this guide, the class and font files, and the
academic CV.

Never tracked: every `applications/<date>-<company>-<type>/` folder — its
`app.tex`, the posting you pasted, and everything in `out/` — plus `build/`,
every résumé or cover-letter PDF, and `_to_delete/`. Which companies you applied
to and when is not information a public repo should carry.

Working notes stay out of the repo: `AGENTS.md` (the evidence base and build
rules) and `master/retired-claims.txt` (claims removed from the master, and why)
are both git-ignored. They live on disk, next to the files they describe.

Keep private notes out of `master/facts.tex`.
