# Contributing to argparse_to_md

## Setting up

1. Clone the repository:
   ```
   git clone https://github.com/igrr/argparse_to_md.git
   ```
2. Install the package and the dependencies:
   ```shell
   cd argparse_to_md
   pip install -e '.[dev]'
   ```
3. Install pre-commit tool and use it to set up pre-commit hooks
   ```shell
   pip install pre-commit
   pre-commit install -t pre-commit -t commit-msg
   ```

## Running tests

Existing tests in [test](test/) directory can be run by executing pytest:
```shell
pytest
```

Please add new tests for added functionality or fixed bugs.

## Making commits

This project uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages. You can use [commitizen](https://commitizen-tools.github.io/commitizen/) to help create commit messages:
```shell
cz commit
```

If a pre-commit hook fails, you can repeat the process with the same message after fixing the issue:
```
cz commit --retry
```

## Publishing releases

1. Run commitizen to check that the changelog looks correct:
   ```shell
   cz bump --dry-run
   ```

2. If yes, run commitizen again to update the version and the changelog and  tag the new release:
   ```shell
   cz bump
   ```

3. Push the commit and the tag to Github:
   ```shell
   git push --follow-tags origin main
   ```
