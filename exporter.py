import jsonlines
import os
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


def authorize():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    flow = InstalledAppFlow.from_client_secrets_file('atoken.json', SCOPES)
    # Prompt user for consent, this will open a web browser for user login and consent.
    flow.run_local_server(port=0, prompt='consent')
    creds = flow.credentials
    return creds

creds = authorize()

service = build('gmail', 'v1', credentials=creds)


def get_all_messages():
    # retrieve messages in batches of 500
    message_ids = []
    next_page_token = ''
 #   count = 0 # Unlimited: comment out this line
    query = 'from:me' # to only get emails I sent
    while next_page_token is not None: #and count < 100: # Unlimited: remove "and count < 100", add colon after None
        results = service.users().messages().list(userId='me', pageToken=next_page_token, maxResults=500, q=query).execute() # Limited: change maxResults to a lower number, like 50.
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken', None)
        message_ids.extend([msg['id'] for msg in messages])
#        count += len(messages) # Unlimited: remove this line

    # retrieve the actual message data for each message id
    messages_data = []
    for msg_id in message_ids:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        messages_data.append(message)

    # write messages to jsonlines file
    with jsonlines.open('messages.jsonl', 'w') as writer:
        for message in messages_data:
            writer.write(message)

if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    get_all_messages()
