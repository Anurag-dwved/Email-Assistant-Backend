import os
from dotenv import load_dotenv
import sys
from slack_sdk.errors import SlackApiError

load_dotenv()

class Config:
    """Configuration class for the Email Assistant application."""
    
    # Gmail API Configuration
    GMAIL_CREDENTIALS = "credentials.json"
    GMAIL_TOKEN = "token.json"
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/calendar"
    ]
    
    # OpenAI Configuration
    my_api_key = os.getenv("my_api_key", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Slack Configuration (with Socket Mode support)
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN").strip()
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "").strip()
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#email-notifications")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///emails.db")

    @classmethod
    def validate_config(cls):
        """Validate all required configurations."""
        errors = []
        
        # Validate OpenAI
        if not cls.my_api_key:
            errors.append("gemini api key is missing from .env file")
     # Validate Slack
        if not cls.SLACK_BOT_TOKEN:
            errors.append("SLACK_BOT_TOKEN is missing from .env file")
        elif not cls.SLACK_BOT_TOKEN.startswith("xoxb-"):
            errors.append("Invalid Slack Bot Token format - must start with 'xoxb-'")
            
        if cls.SLACK_APP_TOKEN and not cls.SLACK_APP_TOKEN.startswith("xapp-"):
            errors.append("Invalid Slack App Token format - must start with 'xapp-'")

        # Validate Gmail
        if not os.path.exists(cls.GMAIL_CREDENTIALS):
            errors.append(f"Gmail credentials file not found at: {cls.GMAIL_CREDENTIALS}")

        if errors:
            error_msg = "\n".join(errors)
            print(f"\nConfiguration Errors:\n{error_msg}\n")
            print("Please check your configuration:")
            print("- OpenAI: https://platform.openai.com/account/api-keys")
            print("- Slack: https://api.slack.com/apps")
            print("- Gmail: https://console.cloud.google.com/apis/credentials")
            sys.exit(1)

    @classmethod
    def test_slack_connection(cls):
        """Test Slack API connection."""
        from slack_sdk import WebClient
        
        try:
            client = WebClient(token=cls.SLACK_BOT_TOKEN)
            response = client.auth_test()
            print(f"Slack connection successful to team: {response['team']}")
            return True
        except SlackApiError as e:
            print(f"Slack connection failed: {e.response['error']}")
            return False

# Validate configuration when executed directly
if __name__ == "__main__":
    Config.validate_config()
    if Config.SLACK_BOT_TOKEN:
        Config.test_slack_connection()
    print("All configurations are valid!")