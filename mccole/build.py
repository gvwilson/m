"""Build HTML site from source files."""

import argparse
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from pathlib import Path
import sys


MARKDOWN_EXTENSIONS = [
    "attr_list",
    "def_list",
    "fenced_code",
    "md_in_html",
    "tables"
]


def build(opt):
    """Main driver."""
    files = _find_files(opt)
    markdown, others = _split_files(files)
    opt.out.mkdir(parents=True, exist_ok=True)
    _handle_markdown(opt, markdown)
    _handle_others(opt, others)


def construct_parser(parser):
    """Parse command-line arguments."""
    parser.add_argument("--dst", type=Path, default="docs", help="output directory")
    parser.add_argument("--src", type=Path, default=".", help="root source directory")
    parser.add_argument("--templates", type=Path, default="templates", help="templates directory")


def _find_files(opt):
    """Collect all interesting files."""
    return [path for path in Path(opt.root).glob("**/*.*")]


def _handle_markdown(opt, files):
    """Handle Markdown files."""
    # Render all documents.
    env = Environment(loader=FileSystemLoader(opt.templates))
    for source in files:
        dest = _make_output_path(opt, source)
        html = _render_markdown(opt, env, source)
        dest.write_text(html)


def _handle_others(opt, files):
    """Handle copy-only files."""
    for source in files:
        dest = _make_output_path(opt, source)
        content = source.read_bytes()
        dest.write_bytes(content)


def _make_output_path(opt, source):
    """Build output path."""
    if source.suffix == ".md":
        temp = source.with_suffix("").with_suffix(".html")
    else:
        temp = source
    return opt.out / temp.relative_to(opt.root)


def _render_markdown(opt, env, source):
    """Convert Markdown to HTML."""
    content = source.read_text()
    template = env.get_template("page.html")
    html = markdown(content, extensions=MARKDOWN_EXTENSIONS)
    return template.render(content=html)


def _split_files(files):
    """Divide files into categories."""
    markdown = []
    others = []
    for path in files:
        if path.suffix == ".md":
            markdown.append(path)
        else:
            others.append(path)
    return markdown, others


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    construct_parser(parser)
    opt = parser.parse_args()
    build(opt)
