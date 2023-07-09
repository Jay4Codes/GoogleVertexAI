import streamlit as st

import gcloud_services as gs
import client_calendar as cc
import client_gmail as cg

st.title('Google Calendar API')

if st.button("Sign In with Google"):
    user_service, calendar_service, mail_service = gs.get_services()
    st.write("Signed In Successfully")

    events = cc.list_events(calendar_service)
    if not events:
        print('No upcoming events found.')
        st.write('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        st.write(start, event['summary'])

    prompt = st.chat_input("Say something")
    if prompt:
        st.write(f"User has sent the following prompt: {prompt}")

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

        sender = user_service.userinfo().get().execute()['email']

        cc.create_event(calendar_service, event_summary, location,
                        timezone, description, start_date_time, end_date_time)
        st.write("Event Created" + event_summary)
        cg.send_gmail(mail_service, sender, "jay4codes@gmail.com",
                      "Event Created " + event_summary)
