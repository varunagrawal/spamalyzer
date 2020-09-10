"""Module with code specific to gmail service."""

import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = "Spamalyzer"
SCOPES = "https://www.googleapis.com/auth/gmail.readonly"


def get_flags():
    """Get argument flags."""
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    return flags


def get_credentials():
    """Get GMail credentials."""
    flags = get_flags()

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


def get_service(credentials):
    """Get the service object corresponding to GMail."""
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    user = service.users().getProfile(userId="me").execute()
    print("Authenticated user: {0}".format(user["emailAddress"]))

    return service
