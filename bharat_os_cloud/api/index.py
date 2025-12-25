import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google import genai  # NEW: Future-proof SDK
import requests
# 1. Initialize Flask (Fixes "app" is not defined)
app = Flask(__name__)

# 2. Initialize Gemini Client (Fixes "model" is not defined)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_mandi_price(item):
    """Fetches 100% accurate price from Govt Data API"""
    api_key = os.environ.get("DATA_GOV_KEY")
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={api_key}&format=json&filters[commodity]={item}"
    try:
        data = requests.get(url).json()
        record = data['records'][0]
        return f"₹{record['modal_price']} in {record['market']} ({record['district']})"
    except:
        return "Price currently unavailable."

@app.route("/", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    media_url = request.values.get('MediaUrl0')

    # 3. Use the new 'client' logic (Fixes errors)
    prompt = f"Identify the agricultural crop in this text: '{incoming_msg}'. One word only."
    
    # NEW: 2025 Gemini Logic
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    ai_analysis = response.text.strip()

    market_info = get_mandi_price(ai_analysis)

    # 4. Respond via Twilio (Fixes "MessagingResponse" is not defined)
    resp = MessagingResponse()
    resp.message(f"✅ *Bharat Voice OS*\nItem: {ai_analysis}\nPrice: {market_info}")
    return str(resp)

# Required for Vercel routing
if __name__ == "__main__":
    app.run()
