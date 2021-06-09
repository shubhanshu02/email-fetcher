
import re
import csv
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

print('Program Started')
TOTAL = 0
SAVED_EMAILS = set()
CSV_DATA = []


def get_message(messageId: str, service, title: str):
    global SAVED_EMAILS, CSV_DATA

    message = service.users().messages().get(
        userId="me",
        id=messageId,
        format="metadata"
    ).execute()
    payload = message['payload']

    recipent = [head['value']
                for head in payload['headers'] if head['name'] == 'To'][0]

    subject = [head['value']
               for head in payload['headers'] if head['name'] == 'Subject'][0]

    if subject.lower() != title.lower():
        print('\t\t0 emails matched')
        return 0

    snippet = message['snippet']
    labels = message['labelIds']

    emails = re.findall(
        r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", recipent)

    label_list = []
    for label_id in labels:
        label_list.append(
            service.users().labels().get(
                userId="me",
                id=label_id,
            ).execute()['name']
        )

    log_row = str(len(emails)) + ' email'
    if len(emails) > 1:
        log_row += 's'
    print(f'\t\t{log_row} Matched')

    for email in emails:
        SAVED_EMAILS.add(email)
        if [email, subject, snippet, " ".join(label_list)] not in CSV_DATA:
            CSV_DATA.append(
                [email, subject, snippet, " ".join(label_list)])

    return len(emails)


def email_extractor(service, title: str):
    global TOTAL
    next_page = ""
    end = False
    page_number = 1
    query = "in:sent "
    title = title.strip()
    if len(title) > 0:
        query += f"subject: {title}"
    print(f"Query= {query}\n")
    while True:
        fetchedlist = service.users().messages().list(
            userId="me",
            q=query,
            pageToken=next_page,
            maxResults=500
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
            TOTAL += get_message(current['id'], service, title)

        page_number += 1
        if end:
            print('\nCompleted Fetching emails')
            break


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    global TOTAL, SAVED_EMAILS, CSV_DATA
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
    file.close()

    file = open('data.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(["SN", "Email", 'Subject', "Message"])
    serial_num = 1
    for row in CSV_DATA:
        writer.writerow([serial_num, *row])
        serial_num += 1
    file.close()

    print('Emails ids can be found in email.txt in the same directory')
    print('Emails and can be found in data.csv in the same directory')


if __name__ == '__main__':
    main()
