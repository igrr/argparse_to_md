import argparse
import io

from .loader import FunctionLoader
from .markdown_processor import process_markdown


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="argparse_to_md")
    parser.add_argument("files", nargs="+", type=argparse.FileType("r+"), help="Markdown files to update")
    parser.add_argument(
        "--extra-sys-path", nargs="+", help="Extra paths to add to PYTHONPATH before loading the module"
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    loader = FunctionLoader(args.extra_sys_path)

    for in_markdown in args.files:
        out_markdown = io.StringIO()
        process_markdown(in_markdown, out_markdown, loader)
        in_markdown.seek(0)
        in_markdown.truncate()
        in_markdown.write(out_markdown.getvalue())
        in_markdown.close()


main()
