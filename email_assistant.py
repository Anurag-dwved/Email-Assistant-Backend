import time
import json
from datetime import datetime, timedelta
from gmail_service import GmailService
from ai_processor import AIProcessor
from slack_notifier import SlackNotifier
from calendar_service import CalendarService
from models import Session, Email, Attachment
from config import Config
Config.validate_config() 
from sqlalchemy.exc import IntegrityError

class EmailAssistant:
    def __init__(self):
        self.gmail = GmailService()
        self.ai = AIProcessor()
        self.slack = SlackNotifier()
        self.calendar = CalendarService()
        self.db_session = Session()
        self.user_info = {
            "name": "Your Name",
            "position": "Your Position",
            "company": "Your Company"
        }
    
    def run(self, interval=300):
        """Main loop to process emails at regular intervals"""
        print("Email Assistant started. Press Ctrl+C to stop.")
        try:
            while True:
                try:
                    self.process_emails()
                    time.sleep(interval)
                except Exception as e:
                    print(f"Error in processing loop: {str(e)}")
                    time.sleep(60)  # Wait before retrying
        except KeyboardInterrupt:
            print("\nEmail Assistant stopped.")
        finally:
            self.db_session.close()

    def process_emails(self):
        """Fetch and process unread emails"""
        print("\nChecking for new emails...")
        try:
            unread_emails = self.gmail.get_unread_emails()
            
            if not unread_emails:
                print("No new emails found.")
                return
                
            print(f"Found {len(unread_emails)} unread emails")
            
            for email in unread_emails:
                try:
                    email_details = self.gmail.get_email_details(email['id'])
                    parsed_email = self._parse_email(email_details)
                    
                    # Store/update in database
                    stored_email = self._store_email(parsed_email)
                    if not stored_email:
                        continue  # Skip if error occurred
                    
                    # Get thread history for context
                    thread_history = self._get_thread_history(parsed_email['thread_id'])
                    
                    # Analyze with AI
                    analysis = self.ai.analyze_email(
                        parsed_email['body'],
                        thread_history=thread_history
                    )
                    print(f"\nProcessing email from: {parsed_email['sender']}")
                    print(f"Subject: {parsed_email['subject']}")
                    print(f"AI analysis: {json.dumps(analysis, indent=2)}")
                    
                    # Process actions
                    self._handle_actions(analysis, parsed_email)
                    
                except Exception as e:
                    print(f"Error processing email {email.get('id')}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            raise

    def _parse_email(self, email_details):
        """Extract relevant email data"""
        headers = {h['name']: h['value'] for h in email_details['payload']['headers']}
        
        return {
            'id': email_details['id'],
            'thread_id': email_details['thread_id'],
            'sender': headers.get('From', ''),
            'recipients': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'body': email_details['snippet'],
            'timestamp': datetime.now(),
            'is_read': False,
            'labels': None,
            'has_attachment': 'parts' in email_details['payload']
        }

    def _store_email(self, email_data):
        """Save or update email in database"""
        try:
            # Check if email exists
            existing = self.db_session.query(Email).filter_by(id=email_data['id']).first()
            
            if existing:
                # Update existing record
                existing.is_read = email_data['is_read']
                existing.body = email_data['body']  # Update with latest content
                print(f"Updated existing email {email_data['id']}")
            else:
                # Create new record
                email = Email(**email_data)
                self.db_session.add(email)
                print(f"Stored new email {email_data['id']}")
            
            self.db_session.commit()
            return True
            
        except IntegrityError:
            self.db_session.rollback()
            print(f"Duplicate email detected: {email_data['id']}")
            return True
        except Exception as e:
            self.db_session.rollback()
            print(f"Database error storing email: {str(e)}")
            return False

    def _get_thread_history(self, thread_id):
        """Get previous emails in the same thread"""
        try:
            thread_emails = self.db_session.query(Email)\
                .filter_by(thread_id=thread_id)\
                .order_by(Email.timestamp.desc())\
                .limit(3)\
                .all()
            return [e.body for e in thread_emails]
        except Exception as e:
            print(f"Error getting thread history: {str(e)}")
            return None

    def _handle_actions(self, analysis, email):
        """Execute actions based on AI analysis"""
        try:
            if 'schedule' in analysis.get('actions', []):
                self._handle_scheduling(email, analysis)
            
            if 'reply' in analysis.get('actions', []):
                self._handle_reply(email, analysis)
            
            if analysis.get('urgency') == 'high' or 'notify' in analysis.get('actions', []):
                self.slack.send_notification(
                    f"Important email from {email['sender']}\n"
                    f"Subject: {email['subject']}\n"
                    f"Summary: {analysis.get('summary', 'No summary')}"
                )
                
        except Exception as e:
            print(f"Error handling actions: {str(e)}")

    def _handle_scheduling(self, email, analysis):
        """Handle meeting scheduling"""
        print("Scheduling meeting...")
        try:
            # Extract time from email (simplified - in reality you'd parse the email)
            start_time = datetime.now() + timedelta(days=1)  # Default: tomorrow
            attendees = [email['sender']]
            
            event_link = self.calendar.create_event(
                summary=f"Meeting: {email['subject']}",
                start_time=start_time,
                attendees=attendees
            )
            print(f"Calendar event created: {event_link}")
            
        except Exception as e:
            print(f"Error scheduling meeting: {str(e)}")

    def _handle_reply(self, email, analysis):
        """Generate and send email reply"""
        print("Generating reply...")
        try:
            reply = self.ai.generate_reply(analysis, email, self.user_info)
            if reply:
                self.gmail.send_email(
                    to=email['sender'],
                    subject=f"Re: {email['subject']}",
                    body=reply
                )
                print(f"Reply sent to: {email['sender']}")
            else:
                print("No reply generated by AI")
        except Exception as e:
            print(f"Error sending reply: {str(e)}")

if __name__ == "__main__":
    assistant = EmailAssistant()
    assistant.run()