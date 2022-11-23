"""Main code driver."""

#pylint: disable=no-member

import dateutil.parser

import arguments
from spamalyzer import (MESSAGE_FILENAME, get_emails, google_service, mail,
                        statistics)


def main(args):
    """Main function."""
    print("Starting up")

    start_date = dateutil.parser.parse(args.start_date)

    emails = get_emails(start_date)

    print("########## Done going through email! ########## ")

    counter = statistics.get_count(emails)
    print(counter.most_common(args.number_of_domains))

if __name__ == "__main__":
    args = arguments.parse_args()
    main(args)
