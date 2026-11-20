#!/usr/bin/env bash
# Commit the dependency updates to the `deps-update` branch and open (or refresh) one pull request.
# Inputs (env): BASE, RUN_URL, HUGO_CHANGED, HUGO_OLD, HUGO_NEW,
#               THEME_CHANGED, THEME_OLD, THEME_NEW, THEME_COMPARE. Needs GH_TOKEN for gh.
set -euo pipefail

branch=deps-update
parts=()
changes=""

if [ "${HUGO_CHANGED:-false}" = true ]; then
  parts+=("Hugo $HUGO_NEW")
  changes+="- **Hugo** \`$HUGO_OLD\` → \`$HUGO_NEW\` ([release notes](https://github.com/gohugoio/hugo/releases/tag/v$HUGO_NEW)).
  Update your local Hugo before building: \`CGO_ENABLED=1 go install -tags extended github.com/gohugoio/hugo@v$HUGO_NEW\`
"
fi
if [ "${THEME_CHANGED:-false}" = true ]; then
  parts+=("PaperMod ${THEME_NEW##*-}")
  changes+="- **PaperMod** \`$THEME_OLD\` → \`$THEME_NEW\` ([upstream changes]($THEME_COMPARE)).
"
fi
if [ ${#parts[@]} -eq 0 ]; then
  echo "Nothing to update."
  exit 0
fi

title="Update ${parts[0]}${parts[1]:+ and ${parts[1]}}"
body="${changes}
The site built with \`--panicOnWarning\` and passed the internal link check in [this run]($RUN_URL).
Pull requests opened by GitHub Actions do not trigger the PR build, so that run is the check."

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git switch -C "$branch"
git add hugo.toml go.mod go.sum
git commit -m "$title"
git push --force origin "$branch"

if [ "$(gh pr list --head "$branch" --state open --json number --jq length)" -gt 0 ]; then
  gh pr edit "$branch" --title "$title" --body "$body"
else
  gh pr create --base "$BASE" --head "$branch" --title "$title" --body "$body"
fi
