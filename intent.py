# intent.py
def detect_intent(text):
    if "book" in text.lower() and "appointment" in text.lower():
        return "book_appointment"
    return "general"
