import streamlit as st
import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import client_calendar as cc
import client_gmail as cg

st.title('Google Calendar API')

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/userinfo.profile']
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

user_service = build('oauth2', 'v2', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)
mail_service = build('gmail', 'v1', credentials=creds)

events = cc.list_events(calendar_service)
if not events:
    print('No upcoming events found.')
    st.write('No upcoming events found.')

for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'])
    st.write(start, event['summary'])

event_summary = st.text_input("Event Summary", value="New Event")
start_date = st.date_input("Start Date")
start_time = st.time_input("Start Time")
end_date = st.date_input("End Date")
end_time = st.time_input("End Time")
location = st.text_input("Location", value="Online")
timezone = st.text_input("Timezone", value="America/Los_Angeles")
description = st.text_area("Description", value="")

if st.button("Submit"):
    print("Inside Submit")
    start_date = start_date.strftime("%Y-%m-%d")
    start_time = start_time.strftime("%H:%M:%S")
    end_date = end_date.strftime("%Y-%m-%d")
    end_time = end_time.strftime("%H:%M:%S")

    start_date_time = f"{start_date}T{start_time}-07:00"
    end_date_time = f"{end_date}T{end_time}-07:00"

    # sender = user_service.userinfo().get().execute()['email']

    cc.create_event(calendar_service, event_summary, location,
                    timezone, description, start_date_time, end_date_time)
    st.write("Event Created" + event_summary)
    cg.send_gmail(mail_service, "jay4emails@gmail.com", "jay4codes@gmail.com",
                  "Event Created " + event_summary)
