from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

import dateutil.parser
import httplib2
import json
import mail
import os


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
CLIENT_ID = "1030690431676-kqae5can829gp98rt17vkhtrtc2jhols.apps.googleusercontent.com"
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = "Spamalyzer"
MESSAGE_FILENAME = "spamalyzer.ndjson"


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir, "spamalyzer-python.json")
    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print("Storing credentials to " + credential_path)
    return credentials


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    next_page_token = None
    idx = 0
    start_date = dateutil.parser.parse("01 Jul 2017 00:00:00 +0000")
    keep_looping = True

    with open(MESSAGE_FILENAME, "w+") as f:
        while keep_looping:
            results = service.users().messages().list(userId="me", pageToken=next_page_token).execute()  # A dict with all the latest email IDs
            next_page_token = results["nextPageToken"]
            messages = results.get('messages', [])

            for message_ in messages:
                idx += 1
                message = service.users().messages().get(userId="me", id=message_["id"]).execute()
                # message = service.users().messages().get(userId="me", id="15d55e2ecc123ed9").execute()
                # print(json.dumps(message, indent=4))

                if not mail.is_valid(message):
                    continue

                email = mail.Mail(message)
                if email.datetime < start_date:
                    keep_looping = False
                    break

                print("{0}: {1} =={2}== \"{3}\" {4}".format(idx, email.sender, email.sender_email, email.subject, email.datetime))

                # Save the JSON to a newline
                json.dump(email.dict(), f)
                f.write("\n")

    # print(messages)


if __name__ == "__main__":
    main()
