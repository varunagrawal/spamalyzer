"""
Class for objects representing Mail
"""
import base64
import json

import dateutil.parser
import html2text


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
        self.sender_email = ""
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
            if header["name"] == "From":
                sender_sig = header["value"]
                signature = sender_sig.split("<")
                self.sender_email = signature[-1].replace(">", "")
                self.sender = signature[0].strip()
            elif header["name"] == "Subject":
                self.subject = header["value"]
            elif header["name"] == "Date":
                self.datetime = dateutil.parser.parse(header["value"])

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
        return ""

    def dict(self):
        """Convert to dictionary representation."""
        body = {
            "id": self.message_id,
            "sender": self.sender,
            "sender_email": self.sender_email,
            "subject": self.subject,
            "date": self.datetime.timestamp(),
            "body": self.body
        }
        return body

    def json(self):
        """Convert to json format."""
        body = self.dict()
        return json.dumps(body)
