# Email Extractor

An email extractor made with Python, which uses Gmail API to fetch email ids from the SENT emails
in the GMAIL account of the user with a given title.

### Dependencies

Run the following command to install the dependencies.

```sh
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage Instructions

1. Create a Google Cloud Project and enable GMAIL API.
2. Create the OAuth credentials. Follow [this](https://developers.google.com/gmail/api/quickstart/python).

3. Download `credentials.json` and paste the file in the same folder as this folder.
4. Run the program using the following command.
   ```sh
   python3 extractor.py
   ```
5. If running for the first time, you may need to set the redirect URI and login to your GMAIL account.

6. Enter the message title to search and press `Enter`.

7. The list of emails will be saved in the current working directory with the name `emails.txt`.
   The emails, their labels, and snippets can be viewed in `data.csv`
