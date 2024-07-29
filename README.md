## Python Gmail Utility

This repository contains Python script setup that can perform actions on your Gmail Inbox using the Gmail APIs. 

## Tech Stack

1. Python
2. SQLite3
3. SQLAchemy

## Requirements

1. Python 3.11
2. Google Account

## Setup Instructions

1. Download your account's credentials.json by following the link below:
>  https://developers.google.com/workspace/guides/create-credentials
2. Place the json file in the root folder.
3. Create and activate your python virtual environment.
```bash
pip3 install virtualenv
python -m virtualenv venv
(Linux) source venv/bin/activate
(Windows) .\venv\Scripts\activate
pip3 install -r requirements.txt
```
4. Configure the values in _config/constants.py_.
```python3
# Number of Mails to operate on for an action
MAIL_COUNT_LIMIT = 10

# If True, will reload the DB with Inbox
LOAD_FLAG = True

# If True, will update the DB with newer mails
UPDATE_FLAG = False
```
6. Modify the _config/rules.json_ to however you need for your utility.
7. Run the command:
```bash
python main.py
```

## Usage
1. When you run the script for the first time, you will be prompted over browser to authenticate with your Gmail Account.
2. A _tokens.json_ file will be stored in the root directory. In production environment, we must encrypt and store it securely.
3. Your emails are stored in the _emails.db_ SQLite database.
4. You can view the output on the terminal, or in the _app.log_ file.
