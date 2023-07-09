from email.message import EmailMessage
import base64


def send_gmail(mail_service, sender, receiver, body):
    print("Inside Send Gmail")
    message = EmailMessage()

    message['To'] = receiver
    message['From'] = sender
    message['Subject'] = "New Appointment Report"
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
        .decode()

    create_message = {
        'raw': encoded_message
    }

    mail_service.users().messages().send(userId='me', body=create_message).execute()

    print("Message sent")
