import argparse
import io

from argparse_to_md.formatter import (
    MarkdownHelpFormatterOptions,
    _build_usage_parts,
    _format_action_md,
    _format_args,
    _format_usage_part,
    _get_metavar,
    _wrap_usage_line,
    gen_argparse_help,
)

# --- _get_metavar ---


def test_get_metavar_explicit():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", metavar="FILE")
    assert _get_metavar(action) == "FILE"


def test_get_metavar_explicit_tuple():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs=2, metavar=("SRC", "DST"))
    assert _get_metavar(action) == ("SRC", "DST")


def test_get_metavar_from_choices():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--mode", choices=["fast", "slow"])
    assert _get_metavar(action) == "{fast,slow}"


def test_get_metavar_optional_default():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo")
    assert _get_metavar(action) == "FOO"


def test_get_metavar_positional_default():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("filename")
    assert _get_metavar(action) == "filename"


# --- _format_args (string metavar) ---


def test_format_args_nargs_none():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo")
    assert _format_args(action, "FOO") == "FOO"


def test_format_args_nargs_optional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="?")
    assert _format_args(action, "FOO") == "[FOO]"


def test_format_args_nargs_zero_or_more():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="*")
    assert _format_args(action, "FOO") == "[FOO ...]"


def test_format_args_nargs_one_or_more():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="+")
    assert _format_args(action, "FOO") == "FOO [FOO ...]"


def test_format_args_nargs_remainder():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("rest", nargs=argparse.REMAINDER)
    assert _format_args(action, "REST") == "..."


def test_format_args_nargs_suppress():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs=argparse.SUPPRESS)
    assert _format_args(action, "FOO") == ""


def test_format_args_nargs_integer():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--coords", nargs=3)
    assert _format_args(action, "N") == "N N N"


# --- _format_args (tuple metavar) ---


def test_format_args_tuple_nargs_none():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo")
    assert _format_args(action, ("SRC",)) == "SRC"


def test_format_args_tuple_nargs_optional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="?")
    assert _format_args(action, ("SRC",)) == "[SRC]"


def test_format_args_tuple_nargs_zero_or_more():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="*")
    assert _format_args(action, ("SRC", "DST")) == "[SRC [DST ...]]"


def test_format_args_tuple_nargs_one_or_more():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", nargs="+")
    assert _format_args(action, ("SRC", "DST")) == "SRC [DST ...]"


def test_format_args_tuple_nargs_integer():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--coords", nargs=3)
    assert _format_args(action, ("X", "Y")) == "X Y Y"


# --- _format_usage_part ---


def test_format_usage_part_simple_optional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo")
    assert _format_usage_part(action) == "[--foo FOO]"


def test_format_usage_part_required_optional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", required=True)
    assert _format_usage_part(action) == "--foo FOO"


def test_format_usage_part_store_true():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--verbose", action="store_true")
    assert _format_usage_part(action) == "[--verbose]"


def test_format_usage_part_positional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("filename")
    assert _format_usage_part(action) == "filename"


def test_format_usage_part_positional_choices():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("action", choices=["start", "stop"])
    assert _format_usage_part(action) == "{start,stop}"


def test_format_usage_part_suppressed():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--secret", help=argparse.SUPPRESS)
    assert _format_usage_part(action) is None


def test_format_usage_part_nargs_plus():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("-i", "--input", nargs="+")
    assert _format_usage_part(action) == "[-i INPUT [INPUT ...]]"


# --- _build_usage_parts ---


def test_build_usage_parts_simple():
    parser = argparse.ArgumentParser()
    parser.add_argument("--foo")
    parser.add_argument("--bar")
    actions = [a for a in parser._actions if a.dest != "help"]
    parts = _build_usage_parts(actions, [])
    assert parts == ["[--foo FOO]", "[--bar BAR]"]


def test_build_usage_parts_mutex_optional():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true")
    group.add_argument("--text", action="store_true")
    actions = [a for a in parser._actions if a.dest != "help"]
    parts = _build_usage_parts(actions, parser._mutually_exclusive_groups)
    assert parts == ["[--json | --text]"]


def test_build_usage_parts_mutex_required():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", action="store_true")
    group.add_argument("--text", action="store_true")
    actions = [a for a in parser._actions if a.dest != "help"]
    parts = _build_usage_parts(actions, parser._mutually_exclusive_groups)
    assert parts == ["(--json | --text)"]


def test_build_usage_parts_mixed():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true")
    group.add_argument("--text", action="store_true")
    parser.add_argument("filename")
    actions = [a for a in parser._actions if a.dest != "help"]
    parts = _build_usage_parts(actions, parser._mutually_exclusive_groups)
    assert parts == ["[--verbose]", "[--json | --text]", "filename"]


# --- _wrap_usage_line ---


def test_wrap_usage_line_short():
    parts = ["[-h]", "[--foo FOO]"]
    result = _wrap_usage_line("prog", parts, 80)
    assert result == "prog [-h] [--foo FOO]"


def test_wrap_usage_line_no_parts():
    result = _wrap_usage_line("prog", [], 80)
    assert result == "prog"


def test_wrap_usage_line_wraps():
    parts = ["[--aaaa AAAA]", "[--bbbb BBBB]", "[--cccc CCCC]"]
    result = _wrap_usage_line("prog", parts, 40)
    assert result == ("prog [--aaaa AAAA] [--bbbb BBBB]\n" "     [--cccc CCCC]")


def test_wrap_usage_line_first_part_always_on_prog_line():
    parts = ["[--very-long-argument VERY_LONG_ARGUMENT]"]
    result = _wrap_usage_line("prog", parts, 20)
    assert result == "prog [--very-long-argument VERY_LONG_ARGUMENT]"


def test_wrap_usage_line_indent_equals_prog_plus_one():
    parts = ["[-h]", "[--foo FOO]", "[--bar BAR]"]
    result = _wrap_usage_line("myprogram", parts, 30)
    lines = result.split("\n")
    assert lines[0].startswith("myprogram ")
    assert lines[1].startswith(" " * (len("myprogram") + 1))


# --- _format_action_md ---


def test_format_action_md_simple_optional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--foo", help="foo help")
    assert _format_action_md(action) == "- `--foo FOO`: foo help\n"


def test_format_action_md_store_true():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("--verbose", action="store_true", help="be verbose")
    assert _format_action_md(action) == "- `--verbose`: be verbose\n"


def test_format_action_md_short_and_long():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    assert _format_action_md(action) == "- `-v`, `--verbose`: be verbose\n"


def test_format_action_md_short_and_long_with_value():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("-o", "--output", help="output file")
    assert _format_action_md(action) == "- `-o OUTPUT`, `--output OUTPUT`: output file\n"


def test_format_action_md_nargs_plus_multiple_opts():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("-i", "--input", nargs="+", help="input files")
    assert _format_action_md(action) == "- `-i INPUT [INPUT ...]`, `--input INPUT [INPUT ...]`: input files\n"


def test_format_action_md_positional():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("filename", help="the file")
    assert _format_action_md(action) == "- `filename`: the file\n"


def test_format_action_md_positional_choices():
    parser = argparse.ArgumentParser()
    action = parser.add_argument("action", choices=["start", "stop"], help="action to run")
    assert _format_action_md(action) == "- {`start`, `stop`}: action to run\n"


# --- gen_argparse_help (integration) ---


def test_gen_argparse_help_basic():
    parser = argparse.ArgumentParser(prog="myprog", description="My program")
    parser.add_argument("--foo", help="foo help")

    out = io.StringIO()
    gen_argparse_help(parser, out, MarkdownHelpFormatterOptions())

    result = out.getvalue()
    assert "Usage:\n```\nmyprog [-h] [--foo FOO]\n```\n" in result
    assert "My program\n" in result
    assert "- `--foo FOO`: foo help\n" in result


def test_gen_argparse_help_with_subheading():
    parser = argparse.ArgumentParser(prog="myprog")
    parser.add_argument("--foo", help="foo help")

    out = io.StringIO()
    gen_argparse_help(parser, out, MarkdownHelpFormatterOptions(subheading_level=2))

    result = out.getvalue()
    assert result.startswith("## Usage:\n")


def test_gen_argparse_help_subparsers():
    parser = argparse.ArgumentParser(prog="myprog")
    subparsers = parser.add_subparsers(dest="cmd", help="command")
    sub = subparsers.add_parser("run", description="run cmd")
    sub.add_argument("--fast", action="store_true", help="go fast")

    out = io.StringIO()
    gen_argparse_help(parser, out, MarkdownHelpFormatterOptions(subheading_level=2))

    result = out.getvalue()
    assert "## Usage of `run`:\n" in result
    assert "- `--fast`: go fast\n" in result
    assert "Optional arguments of `run`:\n" in result


def test_gen_argparse_help_mutex_group():
    parser = argparse.ArgumentParser(prog="myprog")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true", help="output JSON")
    group.add_argument("--text", action="store_true", help="output text")

    out = io.StringIO()
    gen_argparse_help(parser, out, MarkdownHelpFormatterOptions())

    result = out.getvalue()
    assert "[--json | --text]" in result


def test_gen_argparse_help_custom_usage():
    parser = argparse.ArgumentParser(prog="myprog", usage="%(prog)s [options] FILE")
    parser.add_argument("file", help="the file")

    out = io.StringIO()
    gen_argparse_help(parser, out, MarkdownHelpFormatterOptions())

    result = out.getvalue()
    assert "myprog [options] FILE\n" in result
