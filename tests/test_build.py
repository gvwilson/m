"""Test that sites build."""

from argparse import Namespace
from pathlib import Path

import pytest

from mccole.build import build


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
    (tmp_path / "src").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "page.html").write_text(TEMPLATE)
    return tmp_path


def test_build_with_no_files_does_not_create_output_directory(bare_fs):
    dst = bare_fs / "docs"
    opt = Namespace(dst=dst, src=bare_fs / "src", templates=bare_fs / "templates")
    build(opt)
    assert not dst.exists()
