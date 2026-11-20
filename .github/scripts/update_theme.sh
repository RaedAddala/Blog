#!/usr/bin/env bash
# Update the PaperMod Hugo Module to its latest commit (go.mod / go.sum).
# Writes changed/old/new/compare to $GITHUB_OUTPUT, or to stdout when run locally.
set -euo pipefail

MODULE=github.com/adityatelange/hugo-PaperMod
out=${GITHUB_OUTPUT:-/dev/stdout}

version() { grep -oP "^\s*(require\s+)?\Q${MODULE}\E\s+\K\S+" go.mod; }
# A pseudo-version (v0.0.0-<date>-<hash>) ends with the commit hash; a tag is used as-is.
ref() { echo "${1##*-}"; }

old=$(version)
hugo mod get -u "$MODULE"
hugo mod tidy
new=$(version)

if [ "$old" = "$new" ]; then
  echo "changed=false" >>"$out"
  exit 0
fi

{
  echo "changed=true"
  echo "old=$old"
  echo "new=$new"
  echo "compare=https://github.com/adityatelange/hugo-PaperMod/compare/$(ref "$old")...$(ref "$new")"
} >>"$out"
