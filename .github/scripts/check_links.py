#!/usr/bin/env python3
"""Fail if any internal link in the built site points to a file that does not exist.

Checks href, src, srcset and og:/twitter: image URLs in every HTML page. External links are
not fetched (no network, no flaky CI). Usage:

    check_links.py <public-dir> <base-url> [--ignore PATH ...]
"""

import argparse
import posixpath
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

META_IMAGE_KEYS = {"og:image", "twitter:image"}
SKIP_SCHEMES = ("mailto:", "tel:", "data:", "javascript:")


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        srcset = a.get("srcset")
        if srcset:
            self.links.extend(part.strip().split()[0] for part in srcset.split(",") if part.strip())
        if tag == "meta" and (a.get("property") in META_IMAGE_KEYS or a.get("name") in META_IMAGE_KEYS):
            if a.get("content"):
                self.links.append(a["content"])


def target_exists(public: Path, url_path: str) -> bool:
    rel = posixpath.normpath(unquote(url_path)).lstrip("/")
    candidate = public / rel
    if url_path.endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate.is_file()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("public", type=Path)
    ap.add_argument("base_url")
    ap.add_argument("--ignore", action="append", default=[], help="URL path to skip, e.g. /safari-pinned-tab.svg")
    args = ap.parse_args()

    base = urlsplit(args.base_url)
    ignored = set(args.ignore)
    broken = []
    pages = sorted(args.public.rglob("*.html"))

    for page in pages:
        rel_page = page.relative_to(args.public).as_posix()
        page_url = urljoin(args.base_url, rel_page.removesuffix("index.html"))
        collector = LinkCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        for link in collector.links:
            if link.startswith("#") or link.lower().startswith(SKIP_SCHEMES):
                continue
            target = urlsplit(urljoin(page_url, link))
            if target.netloc != base.netloc or target.scheme not in ("http", "https", ""):
                continue  # external: not checked
            if target.path in ignored:
                continue
            if not target_exists(args.public, target.path):
                broken.append((rel_page, link))

    for page, link in broken:
        print(f"BROKEN  {link}  (in {page})")
    print(f"Checked {len(pages)} pages: {len(broken)} broken internal link(s).")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
