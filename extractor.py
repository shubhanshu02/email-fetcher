from __future__ import print_function
import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import re
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

print('Program Started')
TOTAL = 0
SAVED_EMAILS = set()


def get_message(messageId: str, service):
    global SAVED_EMAILS
    headers = service.users().messages().get(
        userId="me",
        id=messageId,
        format="metadata"
    ).execute()['payload']['headers']
    recipent = [head['value']
                for head in headers if head['name'] == 'To'][0]
    emails = re.findall(
        r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", recipent)
    print(f'\t\tFetched {len(emails)} emails')
    for email in emails:
        SAVED_EMAILS.add(email)

    return len(emails)


def email_extractor(service, title: str):
    global TOTAL
    next_page = ""
    end = False
    page_number = 1
    print(f"Query= in:sent {title}\n")
    while True:
        fetchedlist = service.users().messages().list(
            userId="me",
            q=f"in:sent {title}",
            pageToken=next_page,
            maxResults=2  # max = 500
        ).execute()
        print('Page Number', page_number)

        if ('nextPageToken' not in fetchedlist):
            end = True
        else:
            next_page = fetchedlist['nextPageToken']
            # print("\tNext Page token", next_page)

        if 'messages' not in fetchedlist:
            break

        results = fetchedlist['messages']
        print(f'\tFetched {len(results)} messages')

        for current in results:
            TOTAL += get_message(current['id'], service)

        page_number += 1
        if end:
            print('\nCompleted Fetching emails')
            break


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    global TOTAL, SAVED_EMAILS
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    print('Successfully Connected to Google Cloud')
    print('Begin extracting emails\n')
    title = input('Message Title:\t')
    email_extractor(service, title)
    print(f'Fetched total {len(SAVED_EMAILS)} unique emails')
    file = open('emails.txt', 'w')
    for email in SAVED_EMAILS:
        file.write(email+'\n')
    print('Emails can be found in email.txt in the same directory')


if __name__ == '__main__':
    main()
