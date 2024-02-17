import os
import requests
import datetime
from base64 import b64encode
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import pytz

def get_time_entries(email, password, start_date, end_date):
    auth_string = b64encode(f"{email}:{password}".encode()).decode("ascii")
    headers = {'Content-Type': 'application/json', 'Authorization': f'Basic {auth_string}'}
    entries_url = f"https://api.track.toggl.com/api/v9/me/time_entries?start_date={start_date}&end_date={end_date}"
    response = requests.get(entries_url, headers=headers)
    return response.json() if response.ok else None

def insert_event_to_google_calendar(service, event):
    return service.events().insert(calendarId='boji.hit@gmail.com', body=event).execute().get('htmlLink')

def main(request):
    # Load credentials and set up Google Calendar service
    credentials = service_account.Credentials.from_service_account_file('syncToggl.json', scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)

    # Set your Toggl credentials and date range
    email = 'emailforToggl'
    password = 'passwordforToggl'

    # Define the Singapore time zone
    singapore_tz = pytz.timezone('Asia/Singapore')

    # Get the current time in Singapore time zone
    now_in_singapore = datetime.datetime.now(singapore_tz)

    # Calculate the start of the current day in Singapore time zone
    start_of_day_in_singapore = singapore_tz.localize(datetime.datetime(now_in_singapore.year, now_in_singapore.month, now_in_singapore.day, 0, 0, 0))

    # Calculate the end of the current day in Singapore time zone
    end_of_day_in_singapore = singapore_tz.localize(datetime.datetime(now_in_singapore.year, now_in_singapore.month, now_in_singapore.day, 23, 59, 59))

    # Convert start and end times to UTC
    start_date_utc = start_of_day_in_singapore.astimezone(pytz.utc)
    end_date_utc = end_of_day_in_singapore.astimezone(pytz.utc)

    # Format the UTC times in ISO 8601 format
    start_date_utc_str = start_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_utc_str = end_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Fetch Toggl time entries
    time_entries = get_time_entries(email, password, start_date_utc_str, end_date_utc_str)

    # Create Google Calendar events
    for entry in time_entries:
        event = {
            'summary': entry['description'] if 'description' in entry else 'No Description',
            'start': {'dateTime': entry['start'], 'timeZone': 'UTC'},
            'end': {'dateTime': entry['stop'], 'timeZone': 'UTC'},
            'colorId': '11'
        }
        event_link = insert_event_to_google_calendar(service, event)
        print(f'Event created: {event_link}')

    return "Sync completed"

