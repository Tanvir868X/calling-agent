import os
import json
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from dotenv import load_dotenv
import warnings

from google_sheets_logger import log_qa_to_sheet, log_appointment_to_sheet
from appointment_scheduler import is_slot_available

warnings.filterwarnings("ignore", category=FutureWarning)

# Load environment variables
load_dotenv()

PORT = int(os.getenv("PORT", "8080"))
DOMAIN = os.getenv("PUBLIC_DOMAIN")  # e.g., your Render domain like agent.onrender.com
if not DOMAIN:
    raise ValueError("PUBLIC_DOMAIN environment variable not set.")
WS_URL = f"wss://{DOMAIN}/ws"

WELCOME_GREETING = "Hi! I am a Customer agent created by Farhan Tanvir. How can I help you today?!"

SYSTEM_PROMPT = """You are a helpful and friendly voice assistant. This conversation is happening over a phone call, so your responses will be spoken aloud. 
Please follow these rules:
1. Provide clear, concise, and direct answers.
2. Spell out all numbers (e.g., say 'one thousand two hundred' instead of 1200).
3. Avoid special characters like asterisks, bullet points, or emojis.
4. Keep the tone natural and conversational."""

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

sessions = {}

app = FastAPI()

@app.post("/twiml")
async def twiml_endpoint():
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <ConversationRelay 
                url="{WS_URL}" 
                welcomeGreeting="{WELCOME_GREETING}" 
                ttsProvider="ElevenLabs" 
                voice="FGY2WhTYpPnrIDTdsKH5" />
        </Connect>
    </Response>"""
    return Response(content=xml_response, media_type="text/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    call_sid = None

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "setup":
                call_sid = message["callSid"]
                print(f"Call setup: {call_sid}")
                sessions[call_sid] = model.start_chat(history=[])

            elif message["type"] == "prompt":
                if not call_sid or call_sid not in sessions:
                    print(f"Unknown callSid: {call_sid}")
                    continue

                user_prompt = message["voicePrompt"]
                chat = sessions[call_sid]

                # Prompt to Gemini: no phone or reason fields
                prompt_for_gemini = f"""
You will extract structured appointment info from the text if it's related to booking. 
Reply ONLY in JSON format:

{{
  "type": "appointment",
  "name": "John Doe",
  "date": "2025-08-04",
  "time": "2:00 PM"
}}

If the user is not booking, reply:

{{ "type": "qa", "answer": "..." }}

User said: {user_prompt}
"""

                try:
                    response = chat.send_message(prompt_for_gemini)

                    try:
                        parsed = json.loads(response.text)
                    except json.JSONDecodeError:
                        parsed = { "type": "qa", "answer": response.text.strip() }

                    if parsed["type"] == "appointment":
                        name = parsed.get("name", "Unknown")
                        date = parsed.get("date", "")
                        time = parsed.get("time", "")

                        if is_slot_available(date, time):
                            log_appointment_to_sheet(name, date, time)
                            response_text = f"Your appointment has been booked for {date} at {time}."
                        else:
                            response_text = f"Sorry, that slot on {date} at {time} is already booked."
                    else:
                        response_text = parsed["answer"]
                        log_qa_to_sheet(user_prompt, response_text)

                    print(f"User prompt: {user_prompt}")
                    print(f"Response sent: {response_text}")

                except Exception as e:
                    response_text = f"Sorry, I had trouble understanding that. Error: {e}"
                    print(f"❌ Error: {e}")

                await websocket.send_text(
                    json.dumps({
                        "type": "text",
                        "token": response_text,
                        "last": True
                    })
                )

            elif message["type"] == "interrupt":
                print(f"Call interrupted: {call_sid}")

            else:
                print(f"Unhandled message type: {message['type']}")

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for call {call_sid}")
        if call_sid in sessions:
            del sessions[call_sid]
            print(f"Session cleared for {call_sid}")

if __name__ == "__main__":
    print(f"🌐 Server running at: http://localhost:{PORT}")
    print(f"🔗 Twilio should connect to WebSocket at: {WS_URL}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
