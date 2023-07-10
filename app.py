import streamlit as st
import pandas as pd

import gcloud_services as gs
import client_calendar as cc
import client_gmail as cg

import chat
import pl_chat

from streamlit_custom_notification_box import custom_notification_box
from streamlit_option_menu import option_menu

user_service, calendar_service, mail_service = gs.get_services()

st.title('Google Calendar API')

with st.sidebar:
    selected = option_menu(None, ["Home", "Map", "Chat", 'Dashboard'],
                           icons=['house', 'map', 'chat', 'pie'], menu_icon="cast", default_index=1)

    styles = {'material-icons': {'color': 'red'},
              'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
              'notification-text': {'': ''},
              'close-button': {'': ''},
              'link': {'': ''}}


if selected == "Home":
    user_service, calendar_service, mail_service = gs.get_services()
    st.success(user_service.userinfo().get().execute()
               ['name'] + " Signed In Successfully")
    custom_notification_box(icon='info', textDisplay='We are almost done with your registration...',
                            externalLink='more info', url='#', styles=styles, key="foo")

    events = cc.list_events(calendar_service)
    if not events:
        print('No upcoming events found.')
        st.write('No upcoming events found.')

    else:
        df = pd.DataFrame(events)
        new_df = df[['summary', 'location', 'htmlLink', 'start', 'end']]
        new_df["rating"] = 0
        new_df = new_df[['summary',
                         'location', 'rating', 'start', 'end', 'htmlLink', ]]
        edited_df = st.data_editor(
            new_df,
            column_config={
                "rating": st.column_config.NumberColumn(
                    "Your rating",
                    help="How much do you like this command (1-5)?",
                    min_value=1,
                    max_value=5,
                    step=1,
                    format="%d ⭐",
                ),
            },
            hide_index=True,
        )

elif selected == "Map":
    st.map()


elif selected == "Chat":
    pl_chat.export_pl_chat()
    # prompt = st.chat_input("Say something")
    # if prompt:
    #     st.write(f"User has sent the following prompt: {prompt}")

elif selected == "Dashboard":
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

        cc.create_event(calendar_service, event_summary, location,
                        timezone, description, start_date_time, end_date_time)
        st.write("Event Created" + event_summary)
        cg.send_gmail(user_service, mail_service, "jay4codes@gmail.com",
                      "Event Created " + event_summary, location, start_date_time, end_date_time, description)
