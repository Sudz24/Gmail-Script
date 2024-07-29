import unittest
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from handlers.db_handler import DatabaseHandler
from config.models import Base, Email

class TestDatabaseHandler(unittest.TestCase):
    def setUp(self):
        # Create a mock GmailHandler
        self.mock_gmail_handler = Mock()

        # Mock methods for GmailHandler
        self.mock_gmail_handler.fetch_messages.return_value = [
            {'id': 'test-id-1'},
            {'id': 'test-id-2'}
        ]
        self.mock_gmail_handler.fetch_message_by_id.return_value = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Sat, 01 Jan 2022 12:00:00 +0000'},
                    {'name': 'To', 'value': 'recipient@example.com'}
                ],
                'body': {'data': 'VGhpcyBpcyBhIHRlc3QgbWVzc2FnZQ=='}
            }
        }
        self.mock_gmail_handler.get_email_details.return_value = {
            'From': 'test@example.com',
            'Subject': 'Test Subject',
            'Date': 'Sat, 01 Jan 2022 12:00:00 +0000',
            'To': 'recipient@example.com',
            'Message': 'This is a test message'
        }

        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Patch the create_engine and sessionmaker to use the in-memory database
        with patch('database_handler.create_engine', return_value=self.engine), \
             patch('database_handler.sessionmaker', return_value=self.Session):

            self.db_handler = DatabaseHandler(load_flag=True, update_flag=False, gmail_handler=self.mock_gmail_handler)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_save_email_to_db(self):
        session = self.Session()
        email_details = self.mock_gmail_handler.get_email_details(None)
        self.db_handler.save_email_to_db('test-id-1', email_details)

        email = session.query(Email).filter_by(id='test-id-1').one_or_none()
        self.assertIsNotNone(email)
        self.assertEqual(email.from_mail, 'test@example.com')
        self.assertEqual(email.subject, 'Test Subject')
        self.assertEqual(email.date, 'Sat, 01 Jan 2022 12:00:00 +0000')
        self.assertEqual(email.to_mail, 'recipient@example.com')
        self.assertEqual(email.message, 'This is a test message')
        session.close()

    def test_fetch_emails_from_db(self):
        session = self.Session()
        email = Email(
            id='test-id-1',
            from_mail='test@example.com',
            to_mail='recipient@example.com',
            subject='Test Subject',
            date='Sat, 01 Jan 2022 12:00:00 +0000',
            message='This is a test message'
        )
        session.add(email)
        session.commit()

        emails = self.db_handler.fetch_emails_from_db()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0].id, 'test-id-1')
        session.close()

    def test_get_latest_email_date(self):
        session = self.Session()
        email = Email(
            id='test-id-1',
            from_mail='test@example.com',
            to_mail='recipient@example.com',
            subject='Test Subject',
            date='Sat, 01 Jan 2022 12:00:00 +0000',
            message='This is a test message'
        )
        session.add(email)
        session.commit()

        latest_date = self.db_handler.get_latest_email_date()
        self.assertEqual(latest_date, 'Sat, 01 Jan 2022 12:00:00 +0000')
        session.close()

    def test_load_db(self):
        self.db_handler.load_db()
        session = self.Session()
        emails = session.query(Email).all()
        self.assertEqual(len(emails), 2)
        session.close()

    def test_update_db(self):
        session = self.Session()
        email = Email(
            id='test-id-1',
            from_mail='test@example.com',
            to_mail='recipient@example.com',
            subject='Test Subject',
            date='Sat, 01 Jan 2022 12:00:00 +0000',
            message='This is a test message'
        )
        session.add(email)
        session.commit()
        session.close()

        # Mocking the new email that comes after the existing email
        self.mock_gmail_handler.fetch_messages.return_value = [
            {'id': 'test-id-3'}
        ]
        self.mock_gmail_handler.fetch_message_by_id.return_value = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'new@example.com'},
                    {'name': 'Subject', 'value': 'New Test Subject'},
                    {'name': 'Date', 'value': 'Sun, 02 Jan 2022 12:00:00 +0000'},
                    {'name': 'To', 'value': 'new_recipient@example.com'}
                ],
                'body': {'data': 'VGhpcyBpcyBhIG5ldyB0ZXN0IG1lc3NhZ2U='}
            }
        }
        self.mock_gmail_handler.get_email_details.return_value = {
            'From': 'new@example.com',
            'Subject': 'New Test Subject',
            'Date': 'Sun, 02 Jan 2022 12:00:00 +0000',
            'To': 'new_recipient@example.com',
            'Message': 'This is a new test message'
        }
        self.db_handler.update_flag = True
        self.db_handler.update_db()

        session = self.Session()
        emails = session.query(Email).all()
        self.assertEqual(len(emails), 2)
        new_email = session.query(Email).filter_by(id='test-id-3').one_or_none()
        self.assertIsNotNone(new_email)
        self.assertEqual(new_email.from_mail, 'new@example.com')
        self.assertEqual(new_email.subject, 'New Test Subject')
        self.assertEqual(new_email.date, 'Sun, 02 Jan 2022 12:00:00 +0000')
        self.assertEqual(new_email.to_mail, 'new_recipient@example.com')
        self.assertEqual(new_email.message, 'This is a new test message')
        session.close()

    def test_empty_table(self):
        session = self.Session()
        email = Email(
            id='test-id-1',
            from_mail='test@example.com',
            to_mail='recipient@example.com',
            subject='Test Subject',
            date='Sat, 01 Jan 2022 12:00:00 +0000',
            message='This is a test message'
        )
        session.add(email)
        session.commit()
        session.close()

        self.db_handler.empty_table()

        session = self.Session()
        emails = session.query(Email).all()
        self.assertEqual(len(emails), 0)
        session.close()

    def test_table_exists(self):
        self.assertTrue(self.db_handler.table_exists())

if __name__ == '__main__':
    unittest.main()
