import streamlit as st
import pandas as pd
import folium

import gcloud_services as gs
import client_calendar as cc
import client_gmail as cg

import agent_chat
import pl_chat

from streamlit_custom_notification_box import custom_notification_box
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static

user_service, calendar_service, mail_service = gs.get_services()
agent_executor = agent_chat.init_llm()

st.title('Book My Slot')

with st.sidebar:
    profile_image_url = user_service.userinfo().get().execute()['picture']
    st.image(profile_image_url, width=96)
    st.success(user_service.userinfo().get().execute()
               ['name'] + " Signed In Successfully")
    selected = option_menu(None, ["Home", "Chat", "Dashboard"],
                           icons=['house', 'chat', 'map'], menu_icon="cast", default_index=0)

    styles = {'material-icons': {'color': 'red'},
              'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
              'notification-text': {'': ''},
              'close-button': {'': ''},
              'link': {'': ''}}


if selected == "Home":
    user_service, calendar_service, mail_service = gs.get_services()
    custom_notification_box(icon='info', textDisplay='Reminder! for the appointment today at 4:00 PM with Dr. John Doe',
                            externalLink='more info', url='#', styles=styles, key="foo")

    events = cc.list_events(calendar_service)
    if not events:
        print('No upcoming events found.')
        st.write('No upcoming events found.')

    else:
        df = pd.DataFrame(events)
        print(df.columns)
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

elif selected == "Chat":
    # pl_chat.export_pl_chat()

    prompt = st.chat_input("Say something")
    if prompt:
        st.write("👦" + prompt)
        st.write("👩‍💻" + agent_chat.execute_agent(agent_executor, prompt))

    # pl_chat.export_pl_chat()


# elif selected == "Form":
#     event_summary = st.text_input("Event Summary", value="New Event")
#     start_date = st.date_input("Start Date")
#     start_time = st.time_input("Start Time")
#     end_date = st.date_input("End Date")
#     end_time = st.time_input("End Time")
#     location = st.text_input("Location", value="Online")
#     timezone = st.text_input("Timezone", value="Asia/Kolkata")
#     description = st.text_area("Description", value="")

#     if st.button("Submit"):
#         print("Inside Submit")
#         start_date = start_date.strftime("%Y-%m-%d")
#         start_time = start_time.strftime("%H:%M:%S")
#         end_date = end_date.strftime("%Y-%m-%d")
#         end_time = end_time.strftime("%H:%M:%S")

#         start_date_time = f"{start_date}T{start_time}-07:00"
#         end_date_time = f"{end_date}T{end_time}-07:00"

#         cc.create_event(calendar_service, event_summary, location,
#                         timezone, description, start_date_time, end_date_time)
#         st.write("Event Created" + event_summary)
#         cg.send_gmail(user_service, mail_service, "jay4codes@gmail.com",
#                       "Event Created " + event_summary, location, start_date_time, end_date_time, description)

elif "Dashboard":

    # x1 = np.random.randn(200) - 2
    # x2 = np.random.randn(200)
    # x3 = np.random.randn(200) + 2

    # hist_data = [x1, x2, x3]

    # group_labels = ['Group 1', 'Group 2', 'Group 3']
    # fig = ff.create_distplot(
    #     hist_data, group_labels, bin_size=[.1, .25, .5])

    # st.plotly_chart(fig, use_container_width=True)

    mumbai_location = [19.0760, 72.8777]
    folium_map = folium.Map(location=mumbai_location, zoom_start=12)

    restaurant_locations = [
        {"name": "Restaurant 1", "location": [
            19.0741, 72.8629], "appointment_time": "10:00 AM", "summary": "Lunch meeting"},
        {"name": "Restaurant 2", "location": [
            19.0844, 72.8338], "appointment_time": "2:30 PM", "summary": "Team celebration"},
        {"name": "Restaurant 3", "location": [
            19.1102, 72.8262], "appointment_time": "7:00 PM", "summary": "Client dinner"}
    ]

    for restaurant in restaurant_locations:
        tooltip_text = f"Appointment Time: {restaurant['appointment_time']}\nSummary: {restaurant['summary']}"
        folium.Marker(
            location=restaurant["location"],
            popup=restaurant["name"],
            tooltip=tooltip_text,
            icon=folium.Icon(color="blue", icon="cutlery")
        ).add_to(folium_map)

    salon_locations = [
        {"name": "Salon 1", "location": [
            19.0636, 72.8352], "appointment_time": "11:00 AM", "summary": "Haircut"},
        {"name": "Salon 2", "location": [
            19.0778, 72.8419], "appointment_time": "3:00 PM", "summary": "Manicure"},
        {"name": "Salon 3", "location": [
            19.0726, 72.8314], "appointment_time": "6:30 PM", "summary": "Spa session"}
    ]

    for salon in salon_locations:
        tooltip_text = f"Appointment Time: {salon['appointment_time']}\nSummary: {salon['summary']}"
        folium.Marker(
            location=salon["location"],
            popup=salon["name"],
            tooltip=tooltip_text,
            icon=folium.Icon(color="green", icon="scissors")
        ).add_to(folium_map)

    # Display the map using Streamlit
    st.markdown("## Previous Appointments in Mumbai, India")
    st.markdown("### Zoom in to explore")
    folium_static(folium_map)
