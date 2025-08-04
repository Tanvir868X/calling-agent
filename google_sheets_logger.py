import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# Define the required Google API scopes
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Path to your downloaded service account JSON file
CREDENTIALS_FILE = "gspread_creds.json"

# Names of your Google Sheets
QA_SHEET_NAME = "Calling_Agenet_Log"         # Logs Q&A
APPT_SHEET_NAME = "Appointments"             # Logs booked appointments

def get_sheet(sheet_name):
    """Authenticate and return the requested Google Sheet's first worksheet."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1  # First tab
    return sheet

def log_qa_to_sheet(question: str, answer: str):
    """Append a Q&A entry to the log sheet."""
    sheet = get_sheet(QA_SHEET_NAME)
    sheet.append_row([question, answer])
    print(f"Logged Q&A to Google Sheet:\nQ: {question}\nA: {answer}")

def log_appointment_to_sheet(name, date, time):
    """Append an appointment entry to the appointment sheet."""
    sheet = get_sheet(APPT_SHEET_NAME)
    sheet.append_row([
        datetime.now().isoformat(),  # Timestamp
        name,
        date,
        time,
    ])
    print(f"📅 Logged appointment: {name}, {date} at {time}")
