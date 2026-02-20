import argparse
import typing as t
from dataclasses import dataclass

HELP_WIDTH = 100


@dataclass
class MarkdownHelpFormatterOptions:
    subheading_level: int = 0
    pad_lists: bool = False


def _get_metavar(action: argparse.Action) -> t.Union[str, tuple]:
    if action.metavar is not None:
        return action.metavar
    if action.choices is not None:
        return "{" + ",".join(str(c) for c in action.choices) + "}"
    if action.option_strings:
        return action.dest.upper()
    return action.dest


def _format_args(action: argparse.Action, metavar: t.Union[str, tuple]) -> str:
    if isinstance(metavar, tuple):
        if action.nargs is None:
            return str(metavar[0])
        elif action.nargs == argparse.OPTIONAL:
            return "[%s]" % metavar[0]
        elif action.nargs == argparse.ZERO_OR_MORE:
            if len(metavar) == 2:
                return "[%s [%s ...]]" % metavar
            return "[%s ...]" % metavar[0]
        elif action.nargs == argparse.ONE_OR_MORE:
            if len(metavar) == 2:
                return "%s [%s ...]" % metavar
            return "%s [%s ...]" % (metavar[0], metavar[0])
        elif isinstance(action.nargs, int):
            return " ".join(metavar[i] if i < len(metavar) else metavar[-1] for i in range(action.nargs))
        return " ".join(str(m) for m in metavar)

    if action.nargs is None:
        return metavar
    elif action.nargs == argparse.OPTIONAL:
        return "[%s]" % metavar
    elif action.nargs == argparse.ZERO_OR_MORE:
        return "[%s ...]" % metavar
    elif action.nargs == argparse.ONE_OR_MORE:
        return "%s [%s ...]" % (metavar, metavar)
    elif action.nargs == argparse.REMAINDER:
        return "..."
    elif action.nargs == argparse.PARSER:
        return "%s ..." % metavar
    elif action.nargs == argparse.SUPPRESS:
        return ""
    else:
        return " ".join([metavar] * int(action.nargs))


def _is_extend_action(action: argparse.Action) -> bool:
    extend_cls = getattr(argparse, "_ExtendAction", None)
    return extend_cls is not None and isinstance(action, extend_cls)


def _format_usage_part(action: argparse.Action) -> t.Optional[str]:
    if action.help is argparse.SUPPRESS:
        return None

    metavar = _get_metavar(action)

    if not action.option_strings:
        return _format_args(action, metavar)
    else:
        if action.nargs == 0:
            part = action.option_strings[0]
        elif _is_extend_action(action) and action.nargs == argparse.ONE_OR_MORE:
            opt = action.option_strings[0]
            part = "%s %s [%s %s ...]" % (opt, metavar, opt, metavar)
        else:
            args_str = _format_args(action, metavar)
            part = "%s %s" % (action.option_strings[0], args_str)

        if not action.required:
            part = "[%s]" % part
        return part


def _build_usage_parts(actions: list, mutex_groups: list) -> t.List[str]:
    # Map each action to its mutex group (if any)
    action_to_group: t.Dict[int, t.Any] = {}
    for group in mutex_groups:
        for action in group._group_actions:  # pylint: disable=protected-access
            action_to_group[id(action)] = group

    parts: t.List[str] = []
    seen_groups: t.Set[int] = set()

    for action in actions:
        group = action_to_group.get(id(action))

        if group is not None and id(group) not in seen_groups:
            seen_groups.add(id(group))
            group_parts = []
            for group_action in group._group_actions:  # pylint: disable=protected-access
                part = _format_usage_part(group_action)
                if part is not None:
                    # Strip outer [] since the group provides its own brackets
                    if part.startswith("[") and part.endswith("]"):
                        part = part[1:-1]
                    group_parts.append(part)
            if group_parts:
                sep = " | ".join(group_parts)
                if group.required:
                    parts.append("(%s)" % sep)
                else:
                    parts.append("[%s]" % sep)
        elif group is None:
            part = _format_usage_part(action)
            if part is not None:
                parts.append(part)

    return parts


def _wrap_usage_line(prog: str, parts: t.List[str], width: int) -> str:
    if not parts:
        return prog

    single_line = prog + " " + " ".join(parts)
    if len(single_line) <= width:
        return single_line

    continuation_indent = " " * (len(prog) + 1)
    lines: t.List[str] = []
    current_line = prog

    for part in parts:
        candidate = current_line + " " + part
        if len(candidate) <= width or current_line == prog:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = continuation_indent + part

    if current_line.strip():
        lines.append(current_line)

    return "\n".join(lines)


def _format_action_md(action: argparse.Action) -> str:
    metavar = _get_metavar(action)

    if not action.option_strings:
        # Positional
        if isinstance(metavar, str) and metavar.startswith("{") and metavar.endswith("}"):
            inner = metavar[1:-1]
            choices = [c.strip() for c in inner.split(",")]
            invocation = "{" + ", ".join("`%s`" % c for c in choices) + "}"
        else:
            fmt = _format_args(action, metavar) if isinstance(metavar, tuple) else str(metavar)
            invocation = "`%s`" % fmt
    else:
        if action.nargs == 0:
            parts = ["`%s`" % os for os in action.option_strings]
        elif _is_extend_action(action) and action.nargs == argparse.ONE_OR_MORE:
            parts = ["`%s %s [%s %s ...]`" % (os, metavar, os, metavar) for os in action.option_strings]
        else:
            args_str = _format_args(action, metavar)
            parts = ["`%s %s`" % (os, args_str) for os in action.option_strings]
        invocation = ", ".join(parts)

    return "- %s: %s\n" % (invocation, action.help)


def _generate_parser_md(
    parser: argparse.ArgumentParser,
    out: t.TextIO,
    options: MarkdownHelpFormatterOptions,
    usage_label: str,
    group_suffix: str,
) -> None:
    if options.subheading_level > 0:
        subheading_prefix = "#" * options.subheading_level + " "
    else:
        subheading_prefix = ""

    actions = parser._actions  # pylint: disable=protected-access
    mutex_groups = parser._mutually_exclusive_groups  # pylint: disable=protected-access

    optionals = [a for a in actions if a.option_strings]
    positionals = [a for a in actions if not a.option_strings]

    if parser.usage is not None:
        usage_str = parser.usage % dict(prog=parser.prog)
    else:
        parts = _build_usage_parts(optionals + positionals, mutex_groups)
        usage_str = _wrap_usage_line(parser.prog, parts, HELP_WIDTH)

    out.write("%s%s\n```\n%s\n```\n" % (subheading_prefix, usage_label, usage_str))

    if parser.description:
        out.write("%s\n" % parser.description)

    # Normalize group titles
    title_map = {
        "positional arguments": "Positional arguments",
        "optional arguments": "Optional arguments",
        "options": "Optional arguments",
    }

    for group in parser._action_groups:  # pylint: disable=protected-access
        group_actions = [
            a
            for a in group._group_actions  # pylint: disable=protected-access
            if a.dest != "help" and a.help is not argparse.SUPPRESS
        ]
        if not group_actions:
            continue

        title = group.title or ""
        title = title_map.get(title.lower(), title)
        title = "%s%s" % (title, group_suffix)

        out.write("\n%s:\n" % title)
        if options.pad_lists:
            out.write("\n")
        for action in group_actions:
            out.write(_format_action_md(action))


def gen_argparse_help(parser: argparse.ArgumentParser, out_readme: t.TextIO, options: MarkdownHelpFormatterOptions):
    _generate_parser_md(parser, out_readme, options, "Usage:", "")

    subparsers_actions = [
        action
        for action in parser._actions  # pylint: disable=protected-access
        if isinstance(action, argparse._SubParsersAction)  # pylint: disable=protected-access
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            out_readme.write("\n")
            _generate_parser_md(
                subparser,
                out_readme,
                options,
                "Usage of `%s`:\n" % choice,
                " of `%s`" % choice,
            )
