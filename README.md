# Carlos E. Tejada — résumés, cover letters and CV

Everything I send to an employer is built from one master. Facts (titles, dates,
numbers) live in a single file, so every version tells the same story; each
application picks and orders material from the master and adds only its own hook
and "why them".

## Layout

| Path | What it is |
|---|---|
| `resume.master.tex` | The master résumé: every accomplishment, tagged by role type |
| `cover-letter.master.tex` | The master cover letter: five blocks and a paragraph bank |
| `master/facts.tex` | Single source of truth: contact, titles, dates, counts |
| `master/preamble.tex` | Layout and the tagging machinery |
| `cv.tex`, `cv/` | The academic CV (publications, service, supervision) |
| `cv.pdf` | The last published academic CV. `scripts/build.sh cv` writes a fresh one to `build/cv.pdf`; copy it over when you want to publish. |
| `applications/` | One folder per application (git-ignored) |
| `scripts/` | `new-application.sh`, `build.sh`, `preflight.py` |
| `build/` | Master catalog, role-type bases, built CV (git-ignored) |
| `awesome-*.cls`, `fontawesome.sty`, `fonts/` | Awesome-CV template files |

## What is not tracked

This repository is public. Nothing that goes to an employer lives in it: every
application folder, every cover letter and every built résumé PDF is ignored.
What is tracked is the system that produces them — the master files, the facts,
the scripts and the guide.

## Quick start

```sh
scripts/build.sh master     # the catalog: every bullet with its id and role types
scripts/build.sh bases      # one résumé + letter per role type (ds, mle, de, rs, uxr)
scripts/build.sh cv         # the academic CV

scripts/new-application.sh ramp ds "Senior Data Scientist, Growth"
# paste the posting, fill in the app file, then:
scripts/build.sh app applications/2026-09-15-ramp-ds
```

`MASTER.md` is the working guide: the facts to confirm, the role types, how to
tailor an application, the cover-letter structure, and what the pre-send checks
cover.

## License

The Awesome-CV template is MIT. The content is mine.
