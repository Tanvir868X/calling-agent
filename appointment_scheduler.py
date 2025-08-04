from google_sheets_logger import log_appointment_to_sheet
from parse_info import extract_appointment_info

def is_slot_available(date_str, time_str):
    # TODO: Implement real slot checking by reading booked slots from Google Sheets
    # For now, always return True (slot available)
    return True

def book_appointment_from_text(user_text):
    info = extract_appointment_info(user_text)
    
    if not info.get("date") or not info.get("time"):
        return {
            "success": False,
            "message": "I couldn't understand the appointment date or time. Please say something like 'book appointment for August 6th at 2 PM'."
        }

    if is_slot_available(info["date"], info["time"]):
        log_appointment_to_sheet(
            name=info.get("name", "Unknown"),
            date=info["date"],
            time=info["time"]
        )
        return {
            "success": True,
            "message": f"Your appointment has been scheduled for {info['date']} at {info['time']}."
        }
    else:
        return {
            "success": False,
            "message": "That time slot is already taken. Please choose another time."
        }
