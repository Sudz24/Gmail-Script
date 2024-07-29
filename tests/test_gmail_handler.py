import unittest
from unittest.mock import patch, Mock
from googleapiclient.errors import HttpError
from handlers.gmail_handler import GmailHandler

class TestGmailHandler(unittest.TestCase):
    
    @patch('gmail_handler.build')
    @patch('gmail_handler.Credentials')
    @patch('gmail_handler.InstalledAppFlow')
    @patch('gmail_handler.Request')
    def setUp(self, mock_credentials, mock_build):
        self.mock_service = Mock()
        mock_build.return_value = self.mock_service
        
        self.mock_creds = Mock()
        mock_credentials.from_authorized_user_file.return_value = self.mock_creds
        self.mock_creds.valid = True
        
        self.gmail_handler = GmailHandler()

    def test_authenticate_with_token(self):
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            self.gmail_handler.authenticate()
            self.assertTrue(self.gmail_handler.creds)
            self.assertTrue(self.gmail_handler.service)

    def test_fetch_messages(self):
        self.mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test-id'}]
        }
        messages = self.gmail_handler.fetch_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['id'], 'test-id')

    def test_fetch_message_by_id(self):
        self.mock_service.users().messages().get().execute.return_value = {
            'id': 'test-id',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Sat, 01 Jan 2022 12:00:00 +0000'}
                ],
                'body': {'data': 'VGhpcyBpcyBhIHRlc3QgbWVzc2FnZQ=='}
            }
        }
        message = self.gmail_handler.fetch_message_by_id('test-id')
        self.assertEqual(message['id'], 'test-id')

    def test_get_email_details(self):
        message = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Sat, 01 Jan 2022 12:00:00 +0000'}
                ],
                'body': {'data': 'VGhpcyBpcyBhIHRlc3QgbWVzc2FnZQ=='}
            }
        }
        details = self.gmail_handler.get_email_details(message)
        self.assertEqual(details['From'], 'test@example.com')
        self.assertEqual(details['Subject'], 'Test Subject')
        self.assertEqual(details['Date'], 'Sat, 01 Jan 2022 12:00:00 +0000')
        self.assertEqual(details['Message'], 'This is a test message')

    def test_move_to_folder(self):
        self.mock_service.users().labels().list().execute.return_value = {
            'labels': [{'id': 'Label_1', 'name': 'HappyFox'}]
        }
        self.gmail_handler.move_to_folder('test-id', 'HappyFox')
        self.mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id='test-id', body={'addLabelIds': ['Label_1']}
        )

    def test_mark_as_read(self):
        self.gmail_handler.mark_as_read('test-id')
        self.mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id='test-id', body={'removeLabelIds': ['UNREAD']}
        )

    def test_mark_as_unread(self):
        self.gmail_handler.mark_as_unread('test-id')
        self.mock_service.users().messages().modify.assert_called_once_with(
            userId='me', id='test-id', body={'addLabelIds': ['UNREAD']}
        )

if __name__ == '__main__':
    unittest.main()
