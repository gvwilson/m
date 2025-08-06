"""Test that sites build."""

import argparse

from bs4 import BeautifulSoup

from mccole.build import build, construct_parser


def test_build_construct_parser_with_default_values():
    parser = argparse.ArgumentParser()
    construct_parser(parser)
    opt = parser.parse_args([])
    assert all(hasattr(opt, key) for key in ["config", "dst", "src", "templates"])


def test_build_with_no_files_creates_empty_output_directory(bare_fs, opt):
    build(opt)
    dst = bare_fs / opt.dst
    assert dst.is_dir()
    assert len(list(dst.iterdir())) == 0


def test_build_with_single_plain_markdown_file_creates_one_output_file(bare_fs, opt):
    (bare_fs / opt.src / "test.md").write_text("# Title\nbody")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    assert doc.title.string == "Title"
    paragraphs = doc.find_all("p")
    assert len(paragraphs) == 1 and paragraphs[0].string == "body"


def test_build_does_not_copy_dot_files(bare_fs, opt):
    (bare_fs / opt.src / ".gitignore").write_text("content")
    build(opt)
    assert len(list((bare_fs / opt.dst).iterdir())) == 0


def test_build_does_not_copy_dot_dirs(bare_fs, opt):
    (bare_fs / opt.src / ".settings").mkdir()
    build(opt)
    assert len(list((bare_fs / opt.dst).iterdir())) == 0


def test_build_does_not_copy_symlinks(bare_fs, opt):
    (bare_fs / opt.src / "link.lnk").symlink_to("/tmp")
    build(opt)
    assert len(list((bare_fs / opt.dst).iterdir())) == 0


def test_build_does_not_copy_destination_files(bare_fs, opt):
    (bare_fs / opt.dst).mkdir()
    (bare_fs / opt.dst / "existing.html").write_text("<html></html>")
    build(opt)
    assert len(list((bare_fs / opt.dst).iterdir())) == 1


def test_build_does_not_copy_explicitly_skipped_files(bare_fs, opt):
    config_file = bare_fs / opt.config
    config_file.write_text('[tool.mccole]\nskips = ["extras", "uv.lock"]\n')
    (bare_fs / opt.src / "extras").mkdir()
    (bare_fs / opt.src / "extras" / "test.md").write_text("# test")
    (bare_fs / opt.src / "uv.lock").write_text("version = 1")

    build(opt)

    assert len(list((bare_fs / opt.dst).iterdir())) == 0


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


def test_build_boilerplate_links_correctly_adjusted(bare_fs, opt):
    lines = (
        "# Title",
        '<section id="text" markdown="1">',
        "[conduct](./CODE_OF_CONDUCT.md)",
        "[contributing](./CONTRIBUTING.md)",
        "[license](./LICENSE.md)",
        "[home page](./README.md)",
        "</section>",
    )
    (bare_fs / opt.src / "test.md").write_text("\n".join(lines))

    build(opt)

    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    section = doc.select("section[id='text']")[0]
    urls = {node["href"] for node in section.select("a")}
    assert urls == {"./conduct/", "./contrib/", "./license/", "./"}


def test_build_bibliography_links_correctly_adjusted(bare_fs, opt):
    (bare_fs / opt.src / "test.md").write_text("# Title\n[](b:first)\n")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    assert 'href="./bibliography/#first"' in expected.read_text()


def test_build_glossary_links_correctly_adjusted(bare_fs, opt):
    (bare_fs / opt.src / "test.md").write_text("# Title\n[term](g:key)\n")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    assert 'href="./glossary/#key"' in expected.read_text()


def test_build_backtick_code_block_class_applied_to_enclosing_pre(bare_fs, opt):
    (bare_fs / opt.src / "test.md").write_text("# Title\n```py\nx = 1\n```\n")
    build(opt)
    expected = bare_fs / opt.dst / "test.html"
    assert expected.is_file()
    doc = BeautifulSoup(expected.read_text(), "html.parser")
    for tag in ["pre", "code"]:
        nodes = doc.find_all(tag)
        assert len(nodes) == 1
        assert nodes[0]["class"] == ["language-py"]


def test_build_non_markdown_files_copied(bare_fs, opt):
    (bare_fs / opt.src / "in_root.txt").write_text("root text")
    (bare_fs / opt.src / "subdir").mkdir()
    (bare_fs / opt.src / "subdir" / "in_subdir.txt").write_text("subdir text")
    build(opt)
    in_root = bare_fs / opt.dst / "in_root.txt"
    assert in_root.is_file()
    assert in_root.read_text() == "root text"
    in_subdir = bare_fs / opt.dst / "subdir" / "in_subdir.txt"
    assert in_subdir.is_file()
    assert in_subdir.read_text() == "subdir text"


def test_build_warn_unknown_markdown_links(bare_fs, opt, capsys):
    (bare_fs / opt.src / "test.md").write_text("# Title\n[text](link.md)\n")
    build(opt)
    captured = capsys.readouterr()
    assert "unknown Markdown link" in captured.err


def test_build_warn_missing_h1(bare_fs, opt, capsys):
    (bare_fs / opt.src / "test.md").write_text("text\n")
    build(opt)
    captured = capsys.readouterr()
    assert "lacks H1 heading" in captured.err


def test_build_warn_missing_title(bare_fs, opt, capsys):
    template_path = bare_fs / opt.templates / "page.html"
    template = template_path.read_text()
    template = template.replace("<title></title>", "")
    template_path.write_text(template)

    (bare_fs / opt.src / "test.md").write_text("text\n")
    build(opt)
    captured = capsys.readouterr()
    assert "does not have <title> element" in captured.err


def test_build_warn_badly_formatted_config_file(bare_fs, opt, capsys):
    config_file = bare_fs / "pyproject.toml"
    config_file.write_text('[tool.missing]\nskips = ["extras", "uv.lock"]\n')

    build(opt)

    captured = capsys.readouterr()
    assert "does not have 'tool.mccole'" in captured.err


def test_build_warn_overlap_renames_and_skips(bare_fs, opt, capsys):
    config_file = bare_fs / "pyproject.toml"
    config_file.write_text('[tool.mccole]\nskips = ["LICENSE.md"]\n')
    (bare_fs / opt.src / "LICENSE.md").write_text("# License")

    build(opt)

    captured = capsys.readouterr()
    assert "overlap between skips and renames" in captured.err
