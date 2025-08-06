"""Test that sites build."""

from bs4 import BeautifulSoup

from mccole.build import build


def test_build_with_no_files_does_not_create_output_directory(bare_fs, opt):
    build(opt)
    dst = bare_fs / opt.dst
    assert not dst.exists()


def test_build_with_single_plain_markdown_file_creates_one_output_file(bare_fs, opt):
    (bare_fs / opt.src / "test.md").write_text("# Title\nbody")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    assert doc.title.string == "Title"
    paragraphs = doc.find_all("p")
    assert len(paragraphs) == 1 and paragraphs[0].string == "body"


def test_build_boilerplate_files_correctly_renamed(bare_fs, opt):
    fixtures = (
        ("CODE_OF_CONDUCT.md", "Code of Conduct", "conduct"),
        ("CONTRIBUTING.md", "Contributing", "contrib"),
        ("LICENSE.md", "License", "license"),
        ("README.md", "Project", ""),
    )
    for (filename, content, _) in fixtures:
        x = (bare_fs / opt.src / filename)
        x.write_text(f"# {content}\n")

    build(opt)

    for (filename, content, output) in fixtures:
        expected = bare_fs / opt.dst / output / "index.html"
        assert expected.is_file()
        assert content in expected.read_text()


def test_build_backtick_code_block_class_applied_to_enclosing_pre(bare_fs, opt):
    (bare_fs / "test.md").write_text("# Title\n```py\nx = 1\n```\n")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    for tag in ["pre", "code"]:
        nodes = doc.find_all(tag)
        assert len(nodes) == 1
        assert nodes[0]["class"] == ["language-py"]
