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
print('START')


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    # Call the Gmail API
    results = service.users().messages().list(
        userId="me",
        q="in:sent",
        maxResults=10  # max = 500
    ).execute()['messages']

    print(len(results)    )

    for current in results:
        # print('cur:\t',current,results,'\n\n\n')
        # print('ss:\t', current['id'])
        headers = service.users().messages().get(
            userId="me",
            id=current['id'],
            format="metadata"
        ).execute()['payload']['headers']

        recipent = [head['value']
                    for head in headers if head['name'] == 'To'][0]

        emails = re.findall(
            r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", recipent)

        print(
            # json.dumps(
            #    headers, indent=2
            # ),
            *emails
        )

    "subject:Your FlowCrypt Backup"

    # with open('user.json', 'w') as token:
    #    token.write(json.dumps(results))


if __name__ == '__main__':
    main()
