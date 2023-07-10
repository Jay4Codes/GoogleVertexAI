from email.message import EmailMessage
import base64


def send_gmail(user_service, mail_service, receiver, summary, location, startDateTime, endDateTime, description, subject="Appointment Booked"):
    # print("Inside Send Gmail")
    sender = user_service.userinfo().get().execute()['email']
    message = EmailMessage()
    message_text = f'''
    <html>
    <head>
        <title>Appointment Booked</title>
        Hi, <br><br> Your appointment has been booked. Please find the details below: <br><br>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Title</th>
                <th>Location</th>
                <th>Start Date Time</th>
                <th>End Date Time</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>{summary}</td>
                <td>{location}</td>
                <td>{startDateTime}</td>
                <td>{endDateTime}</td>
                <td>{description}</td>
            </tr>
        </table>

        <br><br>
        Thanks,<br>
        Your personal AI Receptionist.
    </body>
    </html>
    '''

    message['To'] = receiver
    message['From'] = sender
    message['Subject'] = subject
    # message.add_header('Content-Type', 'text/html')
    message.add_alternative(message_text, subtype='html')
    # message.set_content(message_text)

    # create_message = {
    #     'raw': base64.urlsafe_b64encode(
    #         f"Content-Type: text/html; charset=utf-8\n\n{message_text}"
    #         .encode('utf-8')
    #     ).decode('utf-8')
    # }

    create_message = {
        'raw': base64.urlsafe_b64encode(message.as_bytes())
        .decode()
    }

    mail_service.users().messages().send(userId='me', body=create_message).execute()

    # print("Message sent")
