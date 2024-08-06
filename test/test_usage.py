import io
from pathlib import Path

from argparse_to_md.loader import FunctionLoader
from argparse_to_md.markdown_processor import process_markdown


def test_usage():
    data_dir = Path(__file__).parent / "data"
    out_md = io.StringIO()
    loader = FunctionLoader(extra_sys_path=[str(data_dir)])
    with open(data_dir / "test1.md.in") as in_md:
        process_markdown(in_md, out_md, loader)

    assert out_md.getvalue() == (data_dir / "test1.md.expected").read_text()
