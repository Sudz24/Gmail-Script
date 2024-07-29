from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from config.constants import MAIL_COUNT_LIMIT
from config.models import Base, Email
from utils.logging_config import logging

class DatabaseHandler:
    def __init__(self, load_flag, update_flag, gmail_handler):

        ''' Init DB Engine '''

        logging.info("Initialising the Database Connection...")

        self.engine = create_engine('sqlite:///emails.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        logging.info("Database successfully connected.\n")

        self.load_flag = load_flag
        self.update_flag = update_flag
        self.gmail_handler = gmail_handler
        self.run()

    def save_email_to_db(self, message_id, details):
        # Add the given Email to the DB

        try:
            session = self.Session()
            email = Email(
                id=message_id,
                from_mail=details.get('From'),
                to_mail=details.get('To'),
                subject=details.get('Subject'),
                date=details.get('Date'),
                message=details.get('Message')
            )
            session.add(email)
            session.commit()
            session.close()
        except IntegrityError:
            logging.info("Duplicate Email Found, Skipping...\n")

    def fetch_emails_from_db(self):

        """Fetch and print all emails from the database."""

        session = self.Session()
        emails = session.query(Email).all()
        session.close()
        return emails

    def get_latest_email_date(self):

        ''' Find the latest email's date from the database '''

        session = self.Session()
        latest_email = session.query(Email).order_by(Email.date.desc()).first()
        latest_date = latest_email.date if latest_email else None
        session.close()
        return latest_date
    
    def load_db(self):

        """Load the database with emails from Gmail API"""

        self.empty_table()  # Empty the table before loading new data

        logging.info("Loading the database with emails from the inbox...")

        messages = self.gmail_handler.fetch_messages(MAIL_COUNT_LIMIT)

        logging.info("Total Emails Found: " + str(len(messages)))

        for message in messages:
            message_id = message['id']
            # Get the Mail
            msg = self.gmail_handler.fetch_message_by_id(message_id)
            # Extract the Mail Details to save in the DB
            email_details = self.gmail_handler.get_email_details(msg)
            # Save it in the DB
            self.save_email_to_db(message_id, email_details)

        logging.info("Done loading all the Emails.\n")

    def update_db(self):

        """Update the database with newer emails from Gmail API."""

        # Get the latest email date from the DB
        latest_date = self.get_latest_email_date().replace(' (UTC)', '')
        if latest_date:
            latest_date = datetime.strptime(latest_date, '%a, %d %b %Y %H:%M:%S %z')

        messages = self.gmail_handler.fetch_messages(MAIL_COUNT_LIMIT)

        for message in messages:
            msg_id = message['id']
            msg = self.gmail_handler.fetch_message_by_id(msg_id)
            email_details = self.gmail_handler.get_email_details(msg)
            email_date = datetime.strptime(email_details['Date'].replace(' (UTC)', ''), '%a, %d %b %Y %H:%M:%S %z')

            # Only insert emails received after the latest DB Email
            if not latest_date or email_date > latest_date:
                self.save_email_to_db(msg_id, email_details)

    def run(self):

        """Run the database operations based on the flags."""

        if not self.table_exists() or self.load_flag:
            self.load_db()
        elif self.update_flag:
            self.update_db()

    def empty_table(self):

        """Empty the emails table in the database."""

        session = self.Session()
        session.query(Email).delete()
        session.commit()
        session.close()

    
    def table_exists(self):

        """Check if the emails table exists in the database."""
        
        inspector = inspect(self.engine)
        return inspector.has_table('emails')

    