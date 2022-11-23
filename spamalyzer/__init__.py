"""Spamalyzer init."""

#pylint: disable=no-member, unspecified-encoding

from spamalyzer import google_service, mail

# This is the Google App ID
CLIENT_ID = "1030690431676-kqae5can829gp98rt17vkhtrtc2jhols.apps.googleusercontent.com"
MESSAGE_FILENAME = "spamalyzer.json"


def get_emails(start_date):
    """Retrieve all emails from the user account
    and write to a JSON file `spamalyzer.json`."""
    credentials = google_service.get_credentials()
    service, user = google_service.get_service(credentials)

    keep_looping = True
    emails = []
    next_page_token = None
    idx = 0

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
                    print(email)

                # Save the JSON to a newline
                # json.dump(email.dict(), messages_file)
                # messages_file.write("\n")

    return emails
