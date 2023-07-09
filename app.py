import streamlit as st
import datetime as dt
import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.message import EmailMessage

st.title('Google Calendar API')

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/gmail.send']
creds = None


if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())


try:
    service = build('calendar', 'v3', credentials=creds)
    mail_service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()

    message.set_content('This is automated draft mail')

    message['To'] = 'jay4codes@gmail.com'
    message['From'] = 'jay4emails@gmail.com'
    message['Subject'] = 'Automated draft'

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
        .decode()

    create_message = {
        'raw': encoded_message
    }

    now = dt.datetime.now().isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        st.write('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        st.write(start, event['summary'])

except HttpError as error:
    print(error)


def create_event(new_event):
    event = service.events().insert(calendarId='primary', body=new_event).execute()
    mail_service.users().messages().send(userId='me', body=create_message).execute()
    print('Event created: %s' % (event.get('htmlLink')))


prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")

new_event = {
    'summary': 'Google I/O 2023',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2023-08-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2023-08-28T17:00:00-09:00',
        'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
    },
}

if st.button("Create Event"):
    create_event(new_event)
