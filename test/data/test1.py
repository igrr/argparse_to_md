import argparse

import module_which_does_not_exist


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='testprog', description='Description of the program')
    parser.add_argument('--foo', help='foo help')
    parser.add_argument('--bar', help='bar help')
    return parser
