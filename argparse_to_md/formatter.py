import argparse
import typing as t


class MarkdownHelpFormatter(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        prefix = "Usage:\n```\n"
        result = super()._format_usage(usage, actions, groups, prefix).rstrip("\n")
        result += "\n```\n"
        return result

    def _format_action(self, action):
        if action.dest == "help":
            return ""
        option_decl = self._format_action_invocation(action)
        option_decl_parts = [od.strip() for od in option_decl.split(",")]
        option_decl_md = ", ".join([f"`{od}`" for od in option_decl_parts])
        return f"- {option_decl_md}: {action.help}\n"


def gen_argparse_help(parser: argparse.ArgumentParser, out_readme: t.TextIO):
    parser.formatter_class = MarkdownHelpFormatter
    parser._optionals.title = "Optional arguments"  # pylint: disable=protected-access
    parser._positionals.title = "Positional arguments"  # pylint: disable=protected-access
    parser.print_help(out_readme)
