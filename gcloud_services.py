import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv


def get_services():
    SCOPES = ['https://www.googleapis.com/auth/calendar',
              'https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email',
              'openid']

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": load_dotenv('CLIENT_ID'),
                        "project_id": load_dotenv('PROJECT_ID'),
                        "auth_uri": load_dotenv('AUTH_URI'),
                        "token_uri": load_dotenv('TOKEN_URI'),
                        "auth_provider_x509_cert_url": load_dotenv('AUTH_PROVIDER_X509_CERT_URL'),
                        "client_secret": load_dotenv('CLIENT_SECRET'),
                        "redirect_uris": [
                            load_dotenv('REDIRECT_URIS')
                        ]
                    }
                },
                SCOPES)
            # flow=InstalledAppFlow.from_client_secrets_file(
            #     'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    user_service = build('oauth2', 'v2', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    mail_service = build('gmail', 'v1', credentials=creds)

    return user_service, calendar_service, mail_service
