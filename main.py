"""Main code driver."""

#pylint: disable=no-member

import argparse
import json

import dateutil.parser

from spamalyzer import get_emails, statistics


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", "-S ", default="01 Jun 2017 00:00:00 +0000",
                        help="Datetime after which to collect emails. E.g. 01 Jun 2017 00:00:00 +0000")
    args = parser.parse_args()
    return args


def main(args):
    """Main function."""
    print("Starting up")

    start_date = dateutil.parser.parse("01 Jun 2018 00:00:00 +0000")

    emails = get_emails(start_date)

    print("########## Done going through email! ########## ")

    counter = statistics.get_count(emails)
    print(counter.most_common(50))


if __name__ == "__main__":
    args = parse_args()
    main(args)
