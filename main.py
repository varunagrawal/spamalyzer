"""Main code driver."""

#pylint: disable=no-member

import json

import dateutil.parser

from spamalyzer import MESSAGE_FILENAME, google_service, mail, statistics


def print_mail(idx, email):
    """Pretty print the email."""
    print("{0:3}: {1:<30.30} | {2:<50} \"{3:60.60}\" {4:>35}".format(idx, email.sender,
                                                                     email.sender_address,
                                                                     email.subject,
                                                                     str(email.datetime)))


def main():
    """Main function."""
    credentials = google_service.get_credentials()
    service = google_service.get_service(credentials)

    next_page_token = None
    idx = 0
    start_date = dateutil.parser.parse("01 Jun 2013 00:00:00 +0000")

    keep_looping = True

    emails = []

    user = service.users().getProfile(userId="me").execute()

    with open(MESSAGE_FILENAME, "w+") as messages_file:
        while keep_looping:
            # A dict with all the latest email IDs
            results = service.users().messages().list(userId="me",
                                                      pageToken=next_page_token).execute()

            next_page_token = results["nextPageToken"]
            messages = results.get('messages', [])

            for message_ in messages:
                idx += 1
                message = service.users().messages().get(
                    userId="me", id=message_["id"]).execute()

                if not mail.is_valid(message):
                    continue

                email = mail.Mail(message)

                if email.datetime < start_date:
                    keep_looping = False
                    break

                # ignore emails that are replies from self.
                if email.sender_address == user['emailAddress']:
                    continue

                if email.is_unread:
                    emails.append(email.sender_address.split('@')[-1])
                    print("{0:4}".format(idx), email)

                # Save the JSON to a newline
                # json.dump(email.dict(), messages_file)
                # messages_file.write("\n")


    print("Done going through email!")

    counter = statistics.get_count(emails)
    print(counter.most_common(50))

if __name__ == "__main__":
    main()
