import io
import subprocess
import sys
from pathlib import Path

from argparse_to_md.loader import FunctionLoader
from argparse_to_md.markdown_processor import process_markdown


def test_usage():
    data_dir = Path(__file__).parent / "data"
    out_md = io.StringIO()
    loader = FunctionLoader()
    with open(data_dir / "test1.md.in") as in_md:
        process_markdown(in_md, out_md, loader)

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
