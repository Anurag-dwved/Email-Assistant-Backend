import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import Config

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        if os.path.exists(Config.GMAIL_TOKEN):
            self.creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN, Config.GMAIL_SCOPES)
        
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.GMAIL_CREDENTIALS, Config.GMAIL_SCOPES)
            self.creds = flow.run_local_server(port=0)
            
            with open(Config.GMAIL_TOKEN, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def get_unread_emails(self, max_results=10):
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=max_results
        ).execute()
        return results.get('messages', [])
    
    def get_email_details(self, msg_id):
        message = self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'payload': message['payload'],
            'snippet': message['snippet']
        }
    
    def send_email(self, to, subject, body):
        message = self._create_message(to, subject, body)
        self.service.users().messages().send(
            userId='me',
            body=message
        ).execute()
    
    def _create_message(self, to, subject, body):
        message = f"From: me\nTo: {to}\nSubject: {subject}\n\n{body}"
        return {'raw': base64.urlsafe_b64encode(message.encode()).decode()}