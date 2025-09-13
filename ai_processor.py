from google.generativeai import GenerativeModel
import google.generativeai as genai
from config import Config
import json



genai.configure(api_key=Config.my_api_key)
client = GenerativeModel("gemini-1.5-flash")


class AIProcessor:
    @staticmethod
    def analyze_email(email_content, thread_history=None):
        """
        Analyze email content using OpenAI's API
        Returns: dict with summary, intent, urgency, and actions
        """
        prompt = f"""
        Analyze this email and provide:
        1. Summary (1-2 sentences)
        2. Intent (what the sender wants)
        3. Urgency (low/medium/high)
        4. Suggested actions (reply, forward, schedule, etc.)
        
        Email Content:
        {email_content}
        
        {f"Thread Context: {thread_history}" if thread_history else ""}
        
        Respond in JSON format with keys: summary, intent, urgency, actions.
        """
        
        try:
            response = client.generate_content(
            prompt,
            generation_config={
            "response_mime_type": "application/json"} )
            # print(response.text)
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            return {
                "summary": "Error analyzing email",
                "intent": "unknown",
                "urgency": "low",
                "actions": []
            }
    
    @staticmethod
    def generate_reply(analysis, original_email, user_info):
        """
        Generate an email reply using OpenAI's API
        Returns: str containing the generated reply
        """
        prompt = f"""
        Compose a professional email reply based on this analysis:
        
        Analysis:
        {json.dumps(analysis, indent=2)}
        
        Original Email:
        From: {original_email['sender']}
        Subject: {original_email['subject']}
        Content: {original_email['body']}
        
        Your Information:
        Name: {user_info['name']}
        Position: {user_info['position']}
        Company: {user_info['company']}
        
        The reply should be concise (3-5 sentences max) and address all key points.
        """
        
        try:
            response = client.generate_content(
                model="gemini-2.0-flash", contents=prompt)
            return response.text
        except Exception as e:
            print(f"Error generating reply: {str(e)}")
            return None