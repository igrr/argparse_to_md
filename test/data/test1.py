import argparse

import module_which_does_not_exist


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='testprog', description='Description of the program')
    parser.add_argument('--foo', help='foo help')
    parser.add_argument('--bar', help='bar help')
    parser.add_argument('--baz', help='baz help')
    parser.add_argument('--longer-argument', help='longer-argument help')
    parser.add_argument('--even-longer-argument', help='even-longer-argument help')

    return parser
