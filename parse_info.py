# parse_info.py
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_appointment_info(user_text):
    prompt = f"""
Extract the following info from this sentence:
- Date
- Time
- Name (if given)
- Reason for the appointment (if any)

Respond in JSON with keys: date, time, name, reason.

Sentence: "{user_text}"
"""
    response = model.generate_content(prompt)
    try:
        return eval(response.text)  # use json.loads() if it's properly formatted
    except:
        return {}
