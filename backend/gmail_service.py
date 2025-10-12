"""
Gmail API Service
Handles Gmail OAuth and email operations
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('GMAIL_REDIRECT_URI')


def create_oauth_flow():
    """Create OAuth 2.0 flow for Gmail"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow


def get_gmail_service(credentials_dict):
    """Create Gmail API service from credentials"""
    credentials = Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    
    service = build('gmail', 'v1', credentials=credentials)
    return service


async def list_emails(credentials_dict, max_results=50, page_token=None):
    """List emails from inbox"""
    try:
        service = get_gmail_service(credentials_dict)
        
        params = {
            'userId': 'me',
            'labelIds': ['INBOX'],
            'maxResults': max_results
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        results = service.users().messages().list(**params).execute()
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')
        
        # Get full message details
        emails = []
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get snippet
            snippet = msg.get('snippet', '')
            
            # Check if unread
            labels = msg.get('labelIds', [])
            is_unread = 'UNREAD' in labels
            
            emails.append({
                'id': msg['id'],
                'threadId': msg['threadId'],
                'subject': subject,
                'from': from_email,
                'date': date,
                'snippet': snippet,
                'unread': is_unread
            })
        
        return {
            'emails': emails,
            'nextPageToken': next_page_token
        }
        
    except HttpError as error:
        logger.error(f'Gmail API error: {error}')
        raise Exception(f'Failed to list emails: {str(error)}')


async def get_email(credentials_dict, message_id):
    """Get full email content"""
    try:
        service = get_gmail_service(credentials_dict)
        
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to_email = next((h['value'] for h in headers if h['name'] == 'To'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Get email body
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        labels = message.get('labelIds', [])
        is_unread = 'UNREAD' in labels
        
        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': subject,
            'from': from_email,
            'to': to_email,
            'date': date,
            'body': body,
            'unread': is_unread
        }
        
    except HttpError as error:
        logger.error(f'Gmail API error: {error}')
        raise Exception(f'Failed to get email: {str(error)}')


async def send_email(credentials_dict, to, subject, body):
    """Send an email"""
    try:
        service = get_gmail_service(credentials_dict)
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            'id': send_message['id'],
            'threadId': send_message['threadId']
        }
        
    except HttpError as error:
        logger.error(f'Gmail API error: {error}')
        raise Exception(f'Failed to send email: {str(error)}')


async def mark_as_read(credentials_dict, message_id):
    """Mark email as read"""
    try:
        service = get_gmail_service(credentials_dict)
        
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return {'success': True}
        
    except HttpError as error:
        logger.error(f'Gmail API error: {error}')
        raise Exception(f'Failed to mark email as read: {str(error)}')
