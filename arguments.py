"""Helpers for command line arguments."""

import argparse


def parse_args():
    """Parse commmand line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_date",
        "-S ",
        default="01 Jun 2017 00:00:00 +0000",
        help=
        "Datetime after which to collect emails. E.g. 01 Jun 2017 00:00:00 +0000"
    )
    parser.add_argument("--upto",
                        default="01 Jun 2022 00:00:00 +0000",
                        help="The datetime upto which to retrieve emails")
    parser.add_argument(
        "--number_of_domains",
        default=50,
        type=int,
        help="The number of domains to display which send the most emails.")

    return parser.parse_args()
