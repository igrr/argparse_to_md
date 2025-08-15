import argparse
import typing as t
from dataclasses import dataclass

HELP_WIDTH = 100


@dataclass
class MarkdownHelpFormatterOptions:
    subheading_level: int = 0


class MarkdownHelpFormatter(argparse.HelpFormatter):
    def __init__(
        self,
        prog,
        indent_increment=2,
        max_help_position=24,
        width=HELP_WIDTH,
        usage_prefix: str = "Usage:",
    ):
        self.usage_prefix = usage_prefix
        super().__init__(prog=prog, indent_increment=indent_increment, max_help_position=max_help_position, width=width)

    def _format_usage(self, usage, actions, groups, prefix):
        prefix = f"{self.usage_prefix}\n```\n"
        result = super()._format_usage(usage, actions, groups, prefix).rstrip("\n")
        result += "\n```\n"
        return result

    def _format_action(self, action):
        if action.dest == "help":
            return ""
        option_decl = self._format_action_invocation(action)
        has_curly_braces = False
        if option_decl.startswith("{") and option_decl.endswith("}"):
            has_curly_braces = True
            option_decl = option_decl[1:-1]

        option_decl_parts = [od.strip() for od in option_decl.split(",")]
        option_decl_md = ", ".join([f"`{od}`" for od in option_decl_parts])
        if has_curly_braces:
            option_decl_md = f"{{{option_decl_md}}}"
        return f"- {option_decl_md}: {action.help}\n"


def get_formatter_with_usage(usage_prefix: str):
    def formatter(prog, indent_increment=2, max_help_position=24, width=HELP_WIDTH):
        return MarkdownHelpFormatter(prog, indent_increment, max_help_position, width, usage_prefix)

    return formatter


def gen_argparse_help(parser: argparse.ArgumentParser, out_readme: t.TextIO, options: MarkdownHelpFormatterOptions):
    if options.subheading_level > 0:
        subheading_prefix = "#" * options.subheading_level + " "
    else:
        subheading_prefix = ""

    parser.formatter_class = get_formatter_with_usage(f"{subheading_prefix}Usage:")
    parser._optionals.title = "Optional arguments"  # pylint: disable=protected-access
    parser._positionals.title = "Positional arguments"  # pylint: disable=protected-access
    parser.print_help(out_readme)

    subparsers_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
    for subparsers_action in subparsers_actions:
        # get all subparsers and print help
        for choice, subparser in subparsers_action.choices.items():
            out_readme.write("\n")
            subparser.formatter_class = get_formatter_with_usage(f"{subheading_prefix}Usage of `{choice}`:\n")
            subparser._optionals.title = f"Optional arguments of `{choice}`"  # pylint: disable=protected-access
            subparser._positionals.title = f"Positional arguments of `{choice}`"  # pylint: disable=protected-access
            subparser.print_help(out_readme)
