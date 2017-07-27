"""
Class for objects representing Mail
"""
import base64
import dateutil.parser
import html2text
import json


def is_valid(message):
    labels = ["CHAT"]
    for label in labels:
        if label in message['labelIds']:
            return False

    return True


class Mail(object):
    def __init__(self, message):
        self.id = message["id"]
        self.snippet = message["snippet"]  # Mail preview seen after the subject
        self.sender_email = ""
        self.sender = ""
        self.subject = ""
        self.body = ""
        self.datetime = None

        self.parse_headers(message["payload"]["headers"])
        self.parse_body(message["payload"])

    def parse_headers(self, headers):
        for header in headers:
            if header["name"] == "From":
                sender_sig = header["value"]
                signature = sender_sig.split(" ")
                self.sender_email = signature[-1][1:-1]
                self.sender = " ".join(signature[:-1])
            elif header["name"] == "Subject":
                self.subject = header["value"]
            elif header["name"] == "Date":
                self.datetime = dateutil.parser.parse(header["value"])

    def parse_body(self, payload):
        if payload["mimeType"] == "multipart/alternative":
            for part in payload["parts"]:
                if part['mimeType'] == 'text/plain':
                    self.body = base64.urlsafe_b64decode(part["body"]["data"]).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    continue
        elif payload["mimeType"] == "text/html":
            self.body = html2text.html2text(base64.urlsafe_b64decode(payload["body"]["data"]).decode('utf-8'))
        elif payload["mimeType"] == "text/plain":
            self.body = base64.urlsafe_b64decode(payload["body"]["data"]).decode('utf-8')

    def __str__(self):
        return ""

    def dict(self):
        body = {
            "id": self.id,
            "sender": self.sender,
            "sender_email": self.sender_email,
            "subject": self.subject,
            "date": self.datetime.timestamp(),
            # "body": self.body
        }
        return body

    def json(self):
        body = self.dict()
        return json.dumps(body)
