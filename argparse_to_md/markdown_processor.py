import os
import re
import typing as t

from .formatter import MarkdownHelpFormatterOptions, gen_argparse_help
from .loader import FunctionLoader


def process_markdown(in_markdown: t.TextIO, out_markdown: t.TextIO, loader: FunctionLoader) -> None:
    """
    Process the input markdown file, updating the argparse help text in the file.

    :param in_markdown: Input markdown file
    :param out_markdown: Output markdown file
    :param loader: FunctionLoader instance to load the argparse factory function
    """
    # Read the input file, processing each line:
    # - if we are not processing a block of argparse help text, just copy the line to the output
    # - if we encounter and argparse_doc comment, start generating argparse help text
    # - skip all lines until we encounter argparse_doc_end comment

    in_argparse_to_md_block = False

    # Match comments like <!--argparse_to_md:test3:get_parser:arg1=val1:arg2=val2-->
    argparse_doc_regex = re.compile(r"<!--\s*argparse_to_md:(?P<module>[\w.]+):(?P<function>\w+)(?P<args>:.*)?\s*-->")
    argparse_doc_end_regex = re.compile(r"<!--\s*argparse_to_md_end\s*-->")

    # Get the current working directory of the input file, so we can add it to the sys.path
    cwd = None
    if hasattr(in_markdown, "name"):
        cwd = os.path.dirname(in_markdown.name)

    for line in in_markdown.readlines():
        if not in_argparse_to_md_block:
            out_markdown.write(line)
            match = argparse_doc_regex.match(line)
            if match:
                in_argparse_to_md_block = True
                module = match.group("module")
                function = match.group("function")
                args = match.group("args")
                parser_factory_function = loader.load_function(module, function, cwd)
                parser = parser_factory_function()
                gen_argparse_help(parser, out_markdown, args_to_options(args))
        else:
            match = argparse_doc_end_regex.match(line)
            if match:
                in_argparse_to_md_block = False
                out_markdown.write(line)
            else:
                continue


def args_to_options(args: str) -> MarkdownHelpFormatterOptions:
    if not args:
        return MarkdownHelpFormatterOptions()

    args = args.strip(":")
    args_dict = {}
    for arg in args.split(":"):
        if "=" not in arg or arg.count("=") != 1:
            raise ValueError(f"Invalid argument format: '{arg}'. Expected format is key=value.")
        key, value = arg.split("=", 1)
        args_dict[key] = value

    subheading_level = 0
    if "subheading_level" in args_dict:
        subheading_level = int(args_dict["subheading_level"])
        del args_dict["subheading_level"]

    pad_lists = False
    if "pad_lists" in args_dict:
        pad_lists = bool(int(args_dict["pad_lists"]))
        del args_dict["pad_lists"]

    if args_dict:
        raise ValueError(f"Unknown arguments: {args_dict}")

    return MarkdownHelpFormatterOptions(subheading_level=subheading_level, pad_lists=pad_lists)
