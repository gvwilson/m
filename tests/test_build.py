"""Test that sites build."""

from bs4 import BeautifulSoup

from mccole.build import build


def test_build_with_no_files_does_not_create_output_directory(bare_fs, opt):
    build(opt)
    dst = bare_fs / opt.dst
    assert not dst.exists()


def test_build_with_single_plain_markdown_file_creates_one_output_file(bare_fs, opt):
    (bare_fs / "test.md").write_text("# Title\nbody")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    assert doc.title.string == "Title"
    paragraphs = doc.find_all("p")
    assert len(paragraphs) == 1 and paragraphs[0].string == "body"


def test_build_with_backtick_code_block(bare_fs, opt):
    (bare_fs / "test.md").write_text("# Title\n```py\nx = 1\n```\n")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    for tag in ["pre", "code"]:
        nodes = doc.find_all(tag)
        assert len(nodes) == 1
        assert nodes[0]["class"] == ["language-py"]
