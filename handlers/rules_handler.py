import json
from utils.logging_config import logging
from datetime import datetime, timedelta
from config.actions import ActionType

"""
The Rules can have all the fields from models.py : 
- from_mail
- date
- to_mail
- subject
- message

The following are the predicates supported:
- contains
- not_contains
- equals
- not_equals
- greater_than
- less_than

The following are the actions supported:
- mark_as_read
- mark_as_unread
- move {additionally requires 'folder' attribute}

"""

class RulesHandler:

    def __init__(self, rules_file):
        self.rules = self.load_rules(rules_file)
        logging.info("Loaded the rules.json\n")

    def load_rules(self, rules_file):

        """Load rules from a JSON file."""

        with open(rules_file, 'r') as file:
            return json.load(file)
        
    def evaluate_rule(self, email, rule):

        """Evaluate a single rule on an email."""

        field_value = getattr(email, rule['field'].lower(), "")

        if rule['predicate'] == 'contains':
            return rule['value'].lower() in field_value.lower()
        
        if rule['predicate'] == 'not_contains':
            return rule['value'].lower() not in field_value.lower()
        
        if rule['predicate'] == 'equals':
            return rule['value'].lower() == field_value.lower()
        
        if rule['predicate'] == 'not_equals':
            return rule['value'].lower() != field_value.lower()
        
        if rule['predicate'] == 'less_than':
            return self.evaluate_date_rule(field_value, rule['value'], 'less_than')
        
        if rule['predicate'] == 'greater_than':
            return self.evaluate_date_rule(field_value, rule['value'], 'greater_than')

        return False
    
    def evaluate_date_rule(self, email_date, rule_value, predicate):

        """Evaluate a date rule on an email."""

        # email_date_str = email_date_str.replace(' (UTC)', '')
        # email_date = datetime.strptime(email_date_str, '%a, %d %b %Y %H:%M:%S %z')
        rule_parts = rule_value.split()
        number = int(rule_parts[0])
        unit = rule_parts[1]

        if unit == 'days':
            cutoff_date = datetime.now() - timedelta(days=number)
        elif unit == 'months':
            cutoff_date = datetime.now() - timedelta(days=number * 30)
        else:
            return False

        if predicate == 'less_than':
            return email_date > cutoff_date
        elif predicate == 'greater_than':
            return email_date < cutoff_date

    def evaluate_rules(self, email):

        """Evaluate all rules on an email."""

        if self.rules['predicate'] == 'all':
            return all(self.evaluate_rule(email, rule) for rule in self.rules['rules'])
        elif self.rules['predicate'] == 'any':
            return any(self.evaluate_rule(email, rule) for rule in self.rules['rules'])
        
        return False
    
    def apply_actions(self, gmail_handler, email):

        """Apply actions on an email based on the rules."""

        for action in self.rules['actions']:
            action_type = ActionType(action['name'])
            if action_type == ActionType.MARK_AS_UNREAD:
                gmail_handler.mark_as_read(email.id)
            elif action_type == ActionType.MOVE:
                gmail_handler.move_to_folder(email.id, action['folder_name'])
            elif action_type == ActionType.MARK_AS_UNREAD:
                gmail_handler.mark_as_unread(email.id)

        logging.info("Successfully finished all actions for the mail!\n")

    def process_emails(self, gmail_handler, emails):

        """Process emails and apply rules/actions."""

        count = 0

        for email in emails:
            if self.evaluate_rules(email):
                logging.info("Rule Passed for email with Subject: " + str(email.subject))
                self.apply_actions(gmail_handler, email)
                count += 1

        logging.info("Total Number of Mail Actions Executed: " + str(count))

