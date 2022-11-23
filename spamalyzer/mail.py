"""
Class for objects representing Mail
"""

#pylint: disable=no-member, unspecified-encoding

import base64
import json

import html2text
from dateutil import parser as dt_parser
from dateutil import tz


def is_valid(message):
    """Check if message is not part of certain invalid labels."""
    invalid_labels_set = {"CHAT"}
    message_labels_set = set(message['labelIds'])
    # return False is set intersection is empty.
    return not bool(message_labels_set.intersection(invalid_labels_set))


def b64_to_utf8_decode(b64_str):
    """Decode base64 string to UTF-8."""
    return base64.urlsafe_b64decode(b64_str).decode('utf-8')


class Mail:
    """Class to represent email message."""

    def __init__(self, message):
        self.message_id = message["id"]
        # Mail preview seen after the subject
        self.snippet = message["snippet"]
        self.sender_address = ""
        self.sender = ""
        self.subject = ""
        self.body = ""
        self.datetime = None

        self.is_unread = "UNREAD" in message['labelIds']

        self.parse_headers(message["payload"]["headers"])
        self.parse_body(message["payload"])

    def parse_headers(self, headers):
        """Parse the mail headers."""
        for header in headers:
            header_key = header["name"].lower()

            if header_key == "from":
                sender_sig = header["value"]
                signature = sender_sig.split("<")
                self.sender_address = signature[-1].replace(">", "")

                sender_name = signature[0].strip()
                if len(sender_name) > 0:
                    self.sender = sender_name
                else:
                    self.sender = self.sender_address.split('@')[0]

            elif header_key == "subject":
                self.subject = header["value"]

            elif header_key == "date":
                # read list of timezone information so that datetime parsing is clean
                tzinfos = json.load(open("spamalyzer/timezoneinfo.json"))
                default_tzinfo = tz.gettz("America/New_York")

                self.datetime = dt_parser.parse(header["value"],
                                                tzinfos=tzinfos,
                                                fuzzy=True)
                # make timezone aware
                self.datetime = self.datetime.replace(
                    tzinfo=self.datetime.tzinfo or default_tzinfo)

    def parse_body(self, payload):
        """Parse the mail body."""
        if payload["mimeType"] == "multipart/alternative":
            for part in payload["parts"]:
                if part['mimeType'] == 'text/plain':
                    self.body = b64_to_utf8_decode(part["body"]["data"])
                elif part['mimeType'] == 'text/html':
                    continue

        elif payload["mimeType"] == "text/html":
            utf_decoded = b64_to_utf8_decode(payload["body"]["data"])
            self.body = html2text.html2text(utf_decoded)

        elif payload["mimeType"] == "text/plain":
            self.body = b64_to_utf8_decode(payload["body"]["data"])

    def __str__(self):
        template = "{0:<25.25} {1:<35.35} {3:>15} || {2:.50}"  # {4:>4}
        return template.format(self.sender, f"<{self.sender_address}>",
                               self.subject, str(self.datetime),
                               '☑' if self.is_unread else '☐')

    def dict(self):
        """Convert to dictionary representation."""
        body = {
            "id": self.message_id,
            "sender": self.sender,
            "sender_address": self.sender_address,
            "subject": self.subject,
            "date": self.datetime.timestamp(),
            # "body": self.body  # no need to save the heavy body
        }
        return body

    def json(self):
        """Convert to json format."""
        body = self.dict()
        return json.dumps(body)
