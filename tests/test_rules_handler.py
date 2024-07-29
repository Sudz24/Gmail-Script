import unittest
from unittest.mock import Mock
from datetime import datetime, timezone, timedelta
from config.models import Email
from handlers.rules_handler import RulesHandler
# from email_message import Email


class TestRulesHandler(unittest.TestCase):
    def setUp(self):
        self.rules_handler = RulesHandler('config/rules.json')
        self.rules_handler.rules = {
            "rules": [
                {
                    "name": "Rule #1",
                    "field": "from_mail",
                    "predicate": "contains",
                    "value": "google"
                },
                {
                    "name": "Rule #2",
                    "field": "date",
                    "predicate": "less_than",
                    "value": "1 days"
                }
            ],
            "predicate": "all",
            "actions": [
                {
                    "name": "mark_as_read"
                },
                {
                    "name": "move",
                    "folder_name": "HappyFox"
                }
            ]
        }

    def test_evaluate_rule_contains(self):
        email = Email(id='test-id', from_mail='test@google.com', subject='Test Subject',
                             date='Sat, 01 Jan 2022 12:00:00 +0000', message='Test Body')
        result = self.rules_handler.evaluate_rule(email, self.rules_handler.rules['rules'][0])
        self.assertTrue(result)

    def test_evaluate_rule_date_less_than(self):
        email = Email(id='test-id', from_mail='test@example.com', subject='Test Subject',
                             date=(datetime.now(timezone.utc) - timedelta(hours=12)).strftime('%a, %d %b %Y %H:%M:%S %z'), message='Test Body')
        result = self.rules_handler.evaluate_rule(email, self.rules_handler.rules['rules'][1])
        self.assertTrue(result)

    def test_evaluate_rules(self):
        email = Email(id='test-id', from_mail='test@google.com', subject='Test Subject',
                             date=(datetime.now(timezone.utc) - timedelta(hours=12)).strftime('%a, %d %b %Y %H:%M:%S %z'), message='Test Body')
        result = self.rules_handler.evaluate_rules(email)
        self.assertTrue(result)

    def test_apply_actions(self):
        gmail_ops_mock = Mock()
        email = Email(id='test-id', from_mail='test@google.com', subject='Test Subject',
                             date='Sat, 01 Jan 2022 12:00:00 +0000', message='Test Body')
        self.rules_handler.apply_actions(gmail_ops_mock, email)
        gmail_ops_mock.mark_as_read.assert_called_once_with('test-id')
        gmail_ops_mock.move_to_folder.assert_called_once_with('test-id', 'HappyFox')


if __name__ == '__main__':
    unittest.main()
