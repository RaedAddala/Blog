#!/usr/bin/env python3
"""Raise [module.hugoVersion] min in hugo.toml to the latest stable Hugo release (never lowers it).

Writes changed/old/new to $GITHUB_OUTPUT, or to stdout when run locally.
Uses $GITHUB_TOKEN for the GitHub API when set (higher rate limit).
"""

import json
import os
import re
import sys
import tomllib
import urllib.request

CONFIG = "hugo.toml"
LATEST_URL = "https://api.github.com/repos/gohugoio/hugo/releases/latest"  # excludes pre-releases
MIN_LINE = re.compile(r'(\[module\.hugoVersion\][^\[]*?\bmin\s*=\s*")([^"]*)(")')


def parse(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.lstrip("v").split("."))


def latest_release() -> str:
    req = urllib.request.Request(LATEST_URL, headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["tag_name"].lstrip("v")


def write_outputs(**values: str) -> None:
    lines = "".join(f"{k}={v}\n" for k, v in values.items())
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a", encoding="utf-8") as f:
            f.write(lines)
    else:
        sys.stdout.write(lines)


def main() -> int:
    with open(CONFIG, encoding="utf-8") as f:
        text = f.read()
    current = tomllib.loads(text)["module"]["hugoVersion"]["min"]
    latest = latest_release()

    if parse(latest) <= parse(current):
        write_outputs(changed="false")
        return 0

    updated, count = MIN_LINE.subn(rf"\g<1>{latest}\g<3>", text, count=1)
    if count != 1 or tomllib.loads(updated)["module"]["hugoVersion"]["min"] != latest:
        sys.exit(f"{CONFIG}: could not update min under [module.hugoVersion]")
    with open(CONFIG, "w", encoding="utf-8") as f:
        f.write(updated)
    write_outputs(changed="true", old=current, new=latest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
