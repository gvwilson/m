"""Check generated HTML."""

import argparse
from pathlib import Path
import sys

from bs4 import BeautifulSoup


def lint(opt):
    """Main driver."""
    filepaths = Path(opt.dst).glob("**/*.html")
    pages = {path: BeautifulSoup(path.read_text(), "html.parser") for path in filepaths}
    for func in [
            lambda o, p: _do_special_links(o, p, "bibliography"),
            lambda o, p: _do_special_links(o, p, "glossary"),
            _do_single_h1
    ]:
        func(opt, pages)


def construct_parser(parser):
    """Parse command-line arguments."""
    parser.add_argument("--dst", type=Path, default="docs", help="output directory")


def _do_single_h1(opt, pages):
    """Check that each page has exactly one <h1>."""
    for path, doc in pages.items():
        titles = doc.find_all("h1")
        _require(len(titles) == 1, f"{len(titles)} H1 elements found in {path}")


def _do_special_links(opt, pages, stem):
    """Check specially-formatted links."""
    source = opt.dst / stem / "index.html"
    if not _require(source in pages, f"{source} not found"):
        return

    defined = {node["id"] for node in pages[source].select("span") if node.has_attr("id")}

    base = f"{stem}/#"
    used = set()
    for path, doc in pages.items():
        here = {
            node["href"].split("#")[-1] for node in doc.select("a[href]") if base in node["href"]
        }
        used |= here
        unknown = here - defined
        _require(len(unknown) == 0, f"unknown {stem} keys in {path}: {', '.join(sorted(unknown))}")

    unused = defined - used
    _require(len(unused) == 0, f"unused {stem} keys: {', '.join(sorted(unused))}")


def _require(cond, msg):
    """Check and report."""
    if not cond:
        print(msg, file=sys.stderr)
    return cond


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    construct_parser(parser)
    opt = parser.parse_args()
    build(opt)
