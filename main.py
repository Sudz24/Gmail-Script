from config.constants import LOAD_FLAG, UPDATE_FLAG
from handlers.db_handler import DatabaseHandler
from handlers.gmail_handler import GmailHandler
from handlers.rules_handler import RulesHandler
from utils.logging_config import logging

try:
    # Init all Handlers
    gmail_handler = GmailHandler()
    database_handler = DatabaseHandler(load_flag=LOAD_FLAG, update_flag=UPDATE_FLAG, gmail_handler=gmail_handler)
    rules_handler = RulesHandler(rules_file='config/rules.json')

    # Check if emails needs to be fetched, and fetch
    emails = database_handler.fetch_emails_from_db()

    # Process All Emails
    rules_handler.process_emails(gmail_handler, emails)
    
except Exception as e:
    logging.error("Oops! There was an issue: ")
    logging.error(str(e))
