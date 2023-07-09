import datetime as dt


def list_events(calendar_service):
    now = dt.datetime.now().isoformat() + 'Z'
    events_result = calendar_service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


def create_event(calendar_service, summary, location, timeZone, description, startDateTime, endDateTime):
    print("Inside CC Create Event")
    new_event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': startDateTime,
            'timeZone': timeZone,
        },
        'end': {
            'dateTime': endDateTime,
            'timeZone': timeZone,
        },
        'reminders': {
            'useDefault': True,
        },
    }

    event = calendar_service.events().insert(
        calendarId='primary', body=new_event).execute()

    print("Event created")

    return event
