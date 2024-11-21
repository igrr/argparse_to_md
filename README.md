# argparse_to_md: Argparse to README.md

![PyPI - Version](https://img.shields.io/pypi/v/argparse-to-md?labelColor=383838)
 [![CI](https://github.com/igrr/argparse_to_md/actions/workflows/main.yml/badge.svg)](https://github.com/igrr/argparse_to_md/actions/workflows/main.yml) ![Python](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/igrr/argparse_to_md/main/.github/workflows/main.yml&query=$.jobs['test'].strategy.matrix['python-version']&label=Python&logo=python&color=3366ff&logoColor=ffcc00&labelColor=383838)

`argparse_to_md` tool helps developers of command-line tools written in Python keep the usage instructions in their README.md files up to date. It can automatically update usage instructions in README.md file based on `argparse` parsers defined in the code. It can be invoked as a pre-commit hook or as a standalone script.

## How to use argparse_to_md:

1. In your CLI tool, move creation of `argparse.ArgumentParser` into a separate function:
    ```python
    import argparse

    def create_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog='mytool')
        parser.add_argument(...)
        return parser

    def main():
        parser = create_parser()
        parser.parse_args()
    ```
2. In your README.md file, add a section where the usage would be described. Replace `mytool` with the fully qualified name of the module and `create_parser` with the name of the function which returns an `argparse.ArgumentParser`.
    ```md
    ### Usage

    <!-- argparse_to_md:mytool:create_parser -->
    <!-- argparse_to_md_end -->
    ```
3. Run `argparse_to_md`, either manually or as a pre-commit hook. The README.md file will be updated, the usage instructions will appear inside this section.
4. Whenever you modify the parser in your code, re-run `argparse_to_md`, or let the pre-commit hook run. README.md will be updated with the new usage instructions.

### Usage as a pre-commit hook

Add to your .pre-commit-config.yaml. This pre-commit hook will be triggered by changes to all Python or Markdown files, and it will edit README.md:

```yaml
repos:
-   repo: https://github.com/igrr/argparse_to_md.git
    rev: v0.3.1
    hooks:
    -   id: argparse_to_md
```

If you need to adjust the list of files to be updated, specify them in `args:` as follows:

```yaml
repos:
-   repo: https://github.com/igrr/argparse_to_md.git
    rev: v0.3.1
    hooks:
    -   id: argparse_to_md
        args: [--input=README.md, --input=README_CN.md]
```

### Command-line usage

You can also use argparse_to_md from the command line:

<!-- argparse_to_md:argparse_to_md.__main__:get_parser -->
Usage:
```
argparse_to_md [-h] [-i INPUT [INPUT ...]]
                          [--extra-sys-path EXTRA_SYS_PATH [EXTRA_SYS_PATH ...]] [--check]
                          [--version]
```

Optional arguments:
- `-i INPUT [INPUT ...]`, `--input INPUT [INPUT ...]`: Markdown file to update (can be specified multiple times).
- `--extra-sys-path EXTRA_SYS_PATH [EXTRA_SYS_PATH ...]`: Extra paths to add to PYTHONPATH before loading the module
- `--check`: Check if the files need to be updated, but don't modify them. Non-zero exit code is returned if any file needs to be updated.
- `--version`: show program's version number and exit
<!-- argparse_to_md_end -->

### Related projects

- https://github.com/9999years/argdown/ — Generates Markdown and RestructuredText from argparse-based parsers.
- https://github.com/alex-rudakov/sphinx-argparse — Sphinx extension for documenting argparse-based parsers.
- https://github.com/docopt/docopt — Inverse of the above, constructs a parser based on documentation.

### License

This tool is Copyright (c) 2024 Ivan Grokhotkov and distributed under the [MIT License](LICENSE).
