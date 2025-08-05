import gspread
import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# Required Google API scopes
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Google Sheets names
QA_SHEET_NAME = "Calling_Agenet_Log"      # Logs Q&A
APPT_SHEET_NAME = "Appointments"          # Logs appointments

def get_sheet(sheet_name):
    """
    Authenticate using JSON from env var and return the first worksheet of the specified sheet.
    """
    # Load JSON credentials from environment variable
    creds_json_str = os.getenv("GSPREAD_CREDS_JSON")
    if not creds_json_str:
        raise ValueError("Missing GSPREAD_CREDS_JSON in environment variables.")

    # Parse and create credentials
    creds_dict = json.loads(creds_json_str)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)

    # Authorize and return sheet
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def log_qa_to_sheet(question: str, answer: str):
    """
    Append a Q&A entry to the Google Sheet.
    """
    sheet = get_sheet(QA_SHEET_NAME)
    sheet.append_row([question, answer])
    print(f"✅ Logged Q&A:\nQ: {question}\nA: {answer}")

def log_appointment_to_sheet(name, date, time):
    """
    Append an appointment entry to the appointments Google Sheet.
    """
    sheet = get_sheet(APPT_SHEET_NAME)
    sheet.append_row([
        datetime.now().isoformat(),  # Timestamp
        name,
        date,
        time,
    ])
    print(f"📅 Logged appointment: {name}, {date} at {time}")
