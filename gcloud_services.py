import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def get_services():

    token = None

    SCOPES = ['https://www.googleapis.com/auth/calendar',
              'https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email',
              'openid']

    creds = None
    # if os.path.exists('token.json'):
    if token:
        # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        creds = Credentials.from_authorized_user_file(token, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": os.getenv("CLIENT_ID"),
                        "project_id": os.getenv("PROJECT_ID"),
                        "auth_uri": os.getenv("AUTH_URI"),
                        "token_uri": os.getenv("TOKEN_URI"),
                        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
                        "client_secret": os.getenv("CLIENT_SECRET"),
                        "redirect_uris": [
                            os.getenv("REDIRECT_URI")
                        ]
                    }
                },
                SCOPES)
            creds = flow.run_local_server(port=0)

        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())
        token = creds.to_json()

    user_service = build('oauth2', 'v2', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    mail_service = build('gmail', 'v1', credentials=creds)

    return user_service, calendar_service, mail_service
