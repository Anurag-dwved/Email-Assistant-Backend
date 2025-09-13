from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config



class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=Config.SLACK_BOT_TOKEN)
    
    def send_notification(self, message):
        try:
            response = self.client.chat_postMessage(
                channel=Config.SLACK_CHANNEL,
                text=message
            )
            return response["ok"]
        except SlackApiError as e:
            print(f"Slack notification failed: {e}")
            return False