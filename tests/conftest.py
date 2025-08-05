"""Test configuration and fixtures."""

from argparse import Namespace

import pytest

CONFIG = """\
[tool.mccole]
skips = []
"""

TEMPLATE = """\
<html>
  <head>
    <title></title>
  </head>
  <body>
{{content}}
  </body>
</html>
"""


@pytest.fixture
def bare_fs(tmp_path):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "page.html").write_text(TEMPLATE)
    (tmp_path / "pyproject.toml").write_text(CONFIG)
    return tmp_path


@pytest.fixture
def opt(bare_fs):
    return Namespace(
        config=bare_fs / "pyproject.toml",
        dst=bare_fs / "docs",
        src=bare_fs,
        templates=bare_fs / "templates",
    )
