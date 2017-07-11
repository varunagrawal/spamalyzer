import os
import httplib2
import base64
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
CLIENT_ID = "1030690431676-kqae5can829gp98rt17vkhtrtc2jhols.apps.googleusercontent.com"
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = "Spamalyzer"


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

    results = service.users().messages().list(userId="me").execute()
    messages = results.get('messages', [])

    for idx, message_ in enumerate(messages):
        message = service.users().messages().get(userId="me", id=message_["id"]).execute()
        # print(json.dumps(message, indent=4))
        
        print("Message ID:" + message["id"])
        print("Snippet:" + message["snippet"])
        for header in message["payload"]["headers"]:
            if header["name"] == "Sender":
                sender_email = header["value"]
            elif header["name"] == "From":
                sender_name = header["value"]
            elif header["name"] == "Subject":
                subject = header["value"]

        print("Number of parts: " + str(len(message["payload"]["parts"])))
        for part in message["payload"]["parts"]:
            print("\n\n\n")
            print(base64.urlsafe_b64decode(part["body"]["data"]).decode('utf-8'))
        # print(message["payload"]["headers"])
        # body = message["payload"]["parts"][0]["body"]["data"]
        # print(base64.urlsafe_b64decode(body).decode('utf-8'))
        break
    # print(messages)


if __name__ == "__main__":
    main()
