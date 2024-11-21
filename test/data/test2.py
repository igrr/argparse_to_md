import argparse

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='testprog')
    parser.add_argument('--foo', help='foo help')

    return parser
