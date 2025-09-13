from googleapiclient.discovery import build
from datetime import datetime, timedelta
from config import Config
from gmail_service import GmailService

class CalendarService:
    def __init__(self):
        self.gmail = GmailService()
        self.service = build('calendar', 'v3', credentials=self.gmail.creds)
    
    def create_event(self, summary, start_time, duration_hours=1, attendees=None):
        end_time = start_time + timedelta(hours=duration_hours)
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees] if attendees else []
        }
        
        event = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return event.get('htmlLink')