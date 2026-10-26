#!/usr/bin/env bash
# Start an application folder:
#   scripts/new-application.sh <company-slug> [role-type] ["Role title, exactly as posted"]
# e.g. scripts/new-application.sh ramp ds "Senior Data Scientist, Growth"
set -euo pipefail
cd "$(dirname "$0")/.."
SLUG="${1:?usage: scripts/new-application.sh <company-slug> [ds|mle|de|rs|uxr] [\"Role title\"]}"
TYPE="${2:-ds}"
ROLE="${3:-Role title, exactly as posted}"
case "$TYPE" in ds|mle|de|rs|uxr) ;; *) echo "Role type must be ds, mle, de, rs or uxr."; exit 1 ;; esac
NAME="$(date +%F)-${SLUG}-${TYPE}"
DIR="applications/$NAME"
[[ -e "$DIR" ]] && { echo "$DIR already exists."; exit 1; }
mkdir -p "$DIR"
COMPANY="$(echo "$SLUG" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"
sed -e "s|^\\\\def\\\\archetype{ds}|\\\\def\\\\archetype{$TYPE}|" \
    -e "s|^\\\\def\\\\Company{Company}|\\\\def\\\\Company{$COMPANY}|" \
    -e "s|^\\\\def\\\\Role{Role title, exactly as posted}|\\\\def\\\\Role{$ROLE}|" \
    applications/_TEMPLATE/app.tex > "$DIR/app.tex"
cp applications/_TEMPLATE/posting.txt "$DIR/posting.txt"
echo "Created $DIR"
echo "  1. Paste the posting into $DIR/posting.txt"
echo "  2. Edit $DIR/app.tex (bullets to drop or add, the letter's hook and why-them)"
echo "  3. scripts/build.sh app $DIR"
