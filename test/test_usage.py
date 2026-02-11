import io
import subprocess
import sys
from pathlib import Path

import pytest

from argparse_to_md.formatter import MarkdownHelpFormatterOptions
from argparse_to_md.loader import FunctionLoader
from argparse_to_md.markdown_processor import args_to_options, process_markdown


def test_usage():
    data_dir = Path(__file__).parent / "data"
    out_md = io.StringIO()
    loader = FunctionLoader()
    with open(data_dir / "test1.md.in") as in_md:
        process_markdown(in_md, out_md, loader)

    with open(data_dir / "test1.md.actual", "w") as actual_md:
        actual_md.write(out_md.getvalue())

    assert out_md.getvalue() == (data_dir / "test1.md.expected").read_text()


def test_cli_check_uage():
    test_dir = Path(__file__).parent

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "argparse_to_md",
            "--check",
            "-i",
            str(test_dir / "data" / "test2.md.in"),
        ],
        text=True,
        capture_output=True,
    )
    output = result.stderr

    assert result.returncode == 2
    assert "Changes required in" in output
    assert "Updating" not in output
    assert "-- `--foo FOO`: foo no help" in output
    assert "+- `--foo FOO`: foo help" in output

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "argparse_to_md",
            "--check",
            "-i",
            str(test_dir / "data" / "test2.md.expected"),
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == ""


def test_subparsers():
    data_dir = Path(__file__).parent / "data"
    out_md = io.StringIO()
    loader = FunctionLoader()
    with open(data_dir / "test3.md.in") as in_md:
        process_markdown(in_md, out_md, loader)

    with open(data_dir / "test3.md.actual", "w") as actual_md:
        actual_md.write(out_md.getvalue())

    assert out_md.getvalue() == (data_dir / "test3.md.expected").read_text()


def test_arguments_to_options():
    assert args_to_options("") == MarkdownHelpFormatterOptions()
    assert args_to_options("subheading_level=2") == MarkdownHelpFormatterOptions(subheading_level=2)
    assert args_to_options("pad_lists=1") == MarkdownHelpFormatterOptions(pad_lists=True)
    assert args_to_options("pad_lists=0") == MarkdownHelpFormatterOptions(pad_lists=False)
    assert args_to_options("subheading_level=2:pad_lists=1") == MarkdownHelpFormatterOptions(
        subheading_level=2, pad_lists=True
    )
    with pytest.raises(ValueError):
        args_to_options("subheading_level=2:foo=bar")
    with pytest.raises(ValueError):
        args_to_options("opt1:opt2")
    with pytest.raises(ValueError):
        args_to_options("opt=val=val2")
