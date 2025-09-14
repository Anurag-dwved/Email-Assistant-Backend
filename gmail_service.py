import os
import base64
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import Config


class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate Gmail using token.json or environment variable.
        On Render, store token.json content in an environment variable (GMAIL_TOKEN_JSON).
        """
        token_path = Config.GMAIL_TOKEN

        # 1. Try environment variable (Render recommended)
        token_env = os.getenv("GMAIL_TOKEN_JSON")
        if token_env:
            self.creds = Credentials.from_authorized_user_info(
                json.loads(token_env), Config.GMAIL_SCOPES
            )

        # 2. Try token.json file (local dev)
        elif os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(
                token_path, Config.GMAIL_SCOPES
            )

        else:
            raise Exception(
                "No Gmail credentials found. Please generate token.json locally and upload it, "
                "or set GMAIL_TOKEN_JSON in environment variables."
            )

        self.service = build("gmail", "v1", credentials=self.creds)

    def get_unread_emails(self, max_results=10):
        results = (
            self.service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
            .execute()
        )
        return results.get("messages", [])

    def get_email_details(self, msg_id):
        message = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        return {
            "id": message["id"],
            "thread_id": message["threadId"],
            "payload": message["payload"],
            "snippet": message["snippet"],
        }

    def send_email(self, to, subject, body):
        message = self._create_message(to, subject, body)
        self.service.users().messages().send(userId="me", body=message).execute()

    def _create_message(self, to, subject, body):
        message = f"From: me\nTo: {to}\nSubject: {subject}\n\n{body}"
        return {"raw": base64.urlsafe_b64encode(message.encode()).decode()}
