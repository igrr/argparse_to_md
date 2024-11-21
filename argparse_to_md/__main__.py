import argparse
import difflib
import io
import sys

from . import __version__
from .loader import FunctionLoader
from .markdown_processor import process_markdown


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="argparse_to_md")
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        type=argparse.FileType("r+"),
        help="Markdown file to update (can be specified multiple times).",
    )
    parser.add_argument(
        "--extra-sys-path", nargs="+", help="Extra paths to add to PYTHONPATH before loading the module"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if the files need to be updated, but don't modify them. "
        "Non-zero exit code is returned if any file needs to be updated.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("No input files specified")

    loader = FunctionLoader(args.extra_sys_path)

    changes_required = False
    for in_markdown in args.input:
        in_markdown_str = in_markdown.read()
        in_markdown.seek(0)
        out_markdown = io.StringIO()
        process_markdown(in_markdown, out_markdown, loader)
        out_markdown_str = out_markdown.getvalue()

        if in_markdown_str != out_markdown_str:
            if args.check:
                print(f"Changes required in {in_markdown.name}:", file=sys.stderr)
                for line in difflib.unified_diff(
                    in_markdown_str.splitlines(), out_markdown_str.splitlines(), lineterm=""
                ):
                    print(line, file=sys.stderr)
                changes_required = True
            else:
                print(f"Updating {in_markdown.name}...", file=sys.stderr)
                in_markdown.seek(0)
                in_markdown.truncate()
                in_markdown.write(out_markdown.getvalue())
                in_markdown.close()

    if args.check and changes_required:
        raise SystemExit(2)


main()
