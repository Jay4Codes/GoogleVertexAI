import streamlit as st
from streamlit_chat import message


def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.past.append(user_input)
    st.session_state.generated.append("The messages from Bot\nWith new line")


def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]


def export_pl_chat():
    table_markdown = '''
Good morning, Arihant! I'd be happy to assist you in finding Italian restaurants in the Powai area. Give me a moment to gather the information for you. 
| Restaurant        | Rating | Price Range |
| ----------------- | ------ | ----------- |
| The Italian Place | 4.5/5  | ₹₹          |
| Pizza Hut         | 4.3/5  | ₹₹₹         |
| Olive Garden      | 4.7/5  | ₹₹₹₹        |
| Papa John's       | 4.2/5  | ₹₹          |
| Domino's Pizza    | 4.4/5  | ₹₹₹         |
    '''

    st.session_state.setdefault(
        'past',
        ["Good morning! I'm looking for some Italian restaurants near me in Powai, Mumbai. Can you help me out?",
         "Thank you for the suggestions! Olive Garden sounds great. Can you please book a table for four people at Olive Garden for tonight at 8pm?",
         "Yes, that's correct!",
         'My name is Arihant.',
         'Sure, my contact number is 9876543210.',
         "No, that's all for now. Thank you so much for your help!"]
    )
    st.session_state.setdefault(
        'generated',
        [{'type': 'normal', 'data': f"{table_markdown}"},
         {'type': 'normal', 'data': f"Certainly, Arihant! I'll take care of that for you. Just to confirm, you would like a table for four people at Olive Garden tonight at 8pm, correct?"},
         {'type': 'normal', 'data': f"Great! I'll proceed with making the reservation for you. May I have your name, please?"},
         {'type': 'normal', 'data': f"Thank you, Arihant. I'm almost done with the booking process. Could you please provide me with a contact number where the restaurant can reach you for any updates?"},
         {'type': 'normal', 'data': f"Thank you for providing your contact number, Arihant. I have successfully made a reservation for four people at Olive Garden tonight at 8pm. They will contact you if needed. Is there anything else I can assist you with?"},
         {'type': 'table', 'data': f"You're welcome, Arihant! If you have any other questions or need further assistance in the future, feel free to ask. Enjoy your meal at Olive Garden tonight!"}]
    )

    chat_placeholder = st.empty()

    with chat_placeholder.container():
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
            message(
                st.session_state['generated'][i]['data'],
                key=f"{i}",
                allow_html=True,
                is_table=True if st.session_state['generated'][i]['type'] == 'table' else False
            )

        st.button("Clear message", on_click=on_btn_click)

    # with st.container():
    #     st.text_input("User Input:", on_change=on_input_change,
    #                   key="user_input")
