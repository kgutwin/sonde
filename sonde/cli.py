import sys
import argparse

import sonde.core


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*',
                        help="CloudFormation templates")

    return parser.parse_args()


def main():
    args = parse_args()
    runner = sonde.core.TestRunner()
    runner.paths = args.paths

    result = runner.run()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
