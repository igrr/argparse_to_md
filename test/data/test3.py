import argparse

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='testprog')
    subparsers = parser.add_subparsers(dest='action', help='action to run')

    foo_action = subparsers.add_parser('foo', description='foo action')
    foo_action.add_argument('--opt1', help='option 1')
    foo_action.add_argument('--opt2', help='option 2')

    bar_action = subparsers.add_parser('bar', description='bar action')
    bar_action.add_argument('--opt3', help='option 3')
    bar_action.add_argument('--opt4', help='option 4')

    parser.add_argument('--opt5', help='option 5')

    return parser

if __name__ == '__main__':
    parser = get_parser()
    parser.parse_args()
