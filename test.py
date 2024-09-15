import os
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import email
import time
from dotenv import load_dotenv
import generate
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import random

import nltk
nltk.download('punkt_tab')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from nrclex import NRCLex

nltk.download('vader_lexicon')

load_dotenv()

CONTEXT = """You are the assistant of Jack's Web Design Ltd.
Your name is Lisa Johnson. 
You are available every Monday and Thursday from 9:00 to 12:00 and from 14:00 to 17:00. In order to make a quote for website, you need to know the following: 
- The number of pages
- The number of languages
- The number of forms
- The number of products

Insist on having payment in advance. No exceptions

The price of the website is $500 per page,, $100 per language, $50 per form and $100 per product.

Don't give out all of the above information at once. Only ask what is required at the time and ask followup questions if necessary."""

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

sia = SentimentIntensityAnalyzer()

def classify_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)

    if sentiment_scores['compound'] >= 0.05:
        return "Positive"
    elif sentiment_scores['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"
    
def detect_prominent_emotion(text):
    emotion = NRCLex(text)

    emotion_scores = emotion.raw_emotion_scores

    if emotion_scores:
        prominent_emotion = max(emotion_scores, key=emotion_scores.get)
        return prominent_emotion
    else:
        return "Normal"
    

    
def prioritize(text):
    vectorizer = joblib.load('vectorizer.joblib')
    classifier = joblib.load('classifier.joblib')
    a = [text]
    
    vectorized = vectorizer.transform(a)
    predicted_priority = classifier.predict(vectorized)
    
    return predicted_priority[0]

def get_services():
    creds = None

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    access_token = os.getenv('GOOGLE_ACCESS_TOKEN')

    if client_id and client_secret and refresh_token and access_token:
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token',
            scopes=SCOPES
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        print("Credentials not found in .env file.")
        return None

    return {
        "gmail": build('gmail', 'v1', credentials=creds),
        "people": build('people', 'v1', credentials=creds),
    }

def get_user_profile(service):
    """Retrieve the user's full name and email address using the People API."""
    try:
        profile = service.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()

        name = profile['names'][0]['displayName']
        email_address = profile['emailAddresses'][0]['value']

        return {"name": name, "email": email_address}
    except Exception as error:
        return None, None


def create_message(sender, to, subject, message_text, headers=None):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if headers:
        for name, value in headers.items():
            message[name] = value
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_message(service, message):
    """Send an email message."""
    try:
        message = (service.users().messages().send(userId='me', body=message).execute())
        print(f"Message Id: {message['id']}")
        return message
    except Exception as error:
        pass
        

def mark_message_as_read(service, message_id):
    """Mark an email message as read."""
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"Message with ID {message_id} marked as read.")
    except Exception as error:
        pass

def get_messages(service):
    message_list = []

    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg_json = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg_json["payload"]["headers"]
        sender_name, sender_email, message_id, subject = "", "", "", ""
        
        for header in headers:
            if header["name"] == "From":
                sender = header["value"]
                sender_name = sender.split("<")[0].strip()
                sender_email = sender.split("<")[1].strip().rstrip(">")
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "Message-ID":
                message_id = header["value"]
        
        raw_message = service.users().messages().get(userId='me', id=message['id'], format="raw").execute()

        message_list.append({
            "sender_name": sender_name,
            "sender_email": sender_email,
            "subject": subject,
            "raw": raw_message['raw'],
            "message_id": message_id  
        })

    return message_list


def get_message_body(raw_message):
    msg_raw = base64.urlsafe_b64decode(raw_message.encode('ASCII'))
    msg_str = email.message_from_bytes(msg_raw)

    if msg_str.is_multipart():
        for part in msg_str.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    else:
        return msg_str.get_payload(decode=True).decode()

def main():
    services = get_services()
    
    gmail_service = services["gmail"]
    people_service = services["people"]
    
    info = get_user_profile(people_service)
    messages = get_messages(gmail_service)  # This now returns the correct message IDs
    
    for message in messages:
        print(f"Processing message from {message['sender_email']} with subject: {message['subject']}")
        raw_email = get_message_body(message['raw'])
        sentiment = classify_sentiment(raw_email)
        emotion = detect_prominent_emotion(raw_email)
        priority = prioritize(raw_email)
        
        reply = generate.make_reply(raw_email, CONTEXT, sentiment, emotion, priority)
        
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        
        sender_name = message["sender_name"]
        sender_email = message["sender_email"]
        subject = message["subject"]
        message_id = message["message_id"]

        reply_block = "\n".join(["> " + line for line in raw_email.split("\n")])

        raw_reply = reply + f"\n\nOn {current_date}, {sender_name} <{sender_email}> wrote:\n\n" + reply_block

        my_info = info["name"] + " <" + info["email"] + ">"

        if not subject.startswith("Re: "):
            subject = "Re: " + subject

        headers = {
            "In-Reply-To": message_id,
            "References": message_id,
        }

        new_message = create_message(my_info, sender_email, subject, raw_reply, headers)

        send_message(gmail_service, new_message)

        print(f"Marking message ID {message_id} as read.")
        
        mark_message_as_read(gmail_service, message_id)



if __name__ == '__main__':
    main()
