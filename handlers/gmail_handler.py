from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import base64
from utils.logging_config import logging

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailHandler:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):

        """Authenticate and create the Gmail API service."""

        logging.info("Performing Authentication...\n")

        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logging.info("tokens.json Found!")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logging.info("Refreshing tokens.json\n")
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        logging.info("Authentication successful!\n")

        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_email_details(self, message):

        """Extract email details from the message object"""

        headers = message.get('payload', {}).get('headers', [])
        details = {}
        for header in headers:
            name = header.get('name')
            value = header.get('value')
            if name == 'From':
                details['From'] = value
            elif name == 'Subject':
                details['Subject'] = value
            elif name == 'Date':
                details['Date'] = value
            elif name == "To":
                details["To"] = value

        # logging.info(message['payload'].keys())
        # print("Done with - " + details['Subject'])

        parts = message.get('payload', {}).get('parts', [])
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    details['Message'] = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            details['Message'] = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')


        # details['Message'] = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        return details
    
    def fetch_messages(self, max_results=10):

        """Fetch messages from Gmail API."""

        query = 'category:primary'
        results = self.service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        messages = results.get('messages', [])
        return messages

    def fetch_message_by_id(self, message_id):

        """Fetch a message by its ID from Gmail API."""

        message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        return message
    
    def move_to_folder(self, message_id, folder_name):

        """Move an email to a specific folder/label."""

        # Get the label ID by folder_name
        label_id = self.get_label_id(folder_name)
        if label_id:
            self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': [label_id]}).execute()
            logging.info("Assigned " + folder_name + " to the Email ID " + str(message_id))
        else:
            logging.warn("Folder Name: \"" + folder_name + "\" not found! Skipping ...")

    def get_label_id(self, label_name):

        """Get label ID by label name."""

        labels = self.service.users().labels().list(userId='me').execute().get('labels', [])

        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
            
        return None
    
    def mark_as_read(self, message_id):

        """Mark an email as read."""

        self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

        logging.info("Email ID \"" + str(message_id) + "\" is marked as READ.")

    def mark_as_unread(self, message_id):

        """Mark an email as read."""

        self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()

        logging.info("Email ID \"" + str(message_id) + "\" is marked as UNREAD.")




