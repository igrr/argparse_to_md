import argparse
import gettext
import typing as t
from argparse import SUPPRESS
from dataclasses import dataclass

_ = gettext.gettext
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


    def start_section(self, heading):
        self._indent()
        section = self._CustomSection(self, self._current_section, heading)
        self._add_item(section.format_help, [])
        self._current_section = section


    class _CustomSection(argparse.HelpFormatter._Section):

        def format_help(self):
            # format the indented section
            if self.parent is not None:
                self.formatter._indent()
            join = self.formatter._join_parts
            item_help = join([func(*args) for func, args in self.items])
            if self.parent is not None:
                self.formatter._dedent()

            # return nothing if the section was empty
            if not item_help:
                return ''

            # add the heading if the section was non-empty
            if self.heading is not SUPPRESS and self.heading is not None:
                current_indent = self.formatter._current_indent
                heading_text = _('%(heading)s:\n') % dict(heading=self.heading)
                heading = '%*s%s\n' % (current_indent, '', heading_text)
            else:
                heading = ''
            # join the section-initial newline, the heading and the help
            return join(['\n', heading, item_help, '\n'])


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
