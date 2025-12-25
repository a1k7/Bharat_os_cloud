import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google import genai  # Ensure 'google-genai' is in requirements.txt

# 1. Initialize Flask (Fixes '"app" is not defined')
app = Flask(__name__)

# 2. Initialize Gemini Client (Fixes '"model" is not defined')
# Vercel will pull the key from your Environment Variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_mandi_price(item):
    """Fetches accurate price from Govt Data API"""
    api_key = os.environ.get("DATA_GOV_KEY")
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={api_key}&format=json&filters[commodity]={item}"
    try:
        response = requests.get(url)
        data = response.json()
        record = data['records'][0]
        return f"₹{record['modal_price']} in {record['market']} ({record['district']})"
    except Exception:
        return "Price currently unavailable."

@app.route("/", methods=['POST'])
def whatsapp_webhook():
    # 3. Handle incoming WhatsApp data
    incoming_msg = request.values.get('Body', '').lower()
    
    # Extract intent using Gemini 1.5 Flash
    prompt = f"Identify the agricultural crop in this text: '{incoming_msg}'. Answer with ONE word only."
    
    try:
        # Use the new 2025 SDK syntax
        result = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        ai_analysis = result.text.strip()
        market_info = get_mandi_price(ai_analysis)
    except Exception as e:
        ai_analysis = "Error"
        market_info = "Could not process request."

    # 4. Create Response (Fixes '"MessagingResponse" is not defined')
    resp = MessagingResponse()
    resp.message(f"✅ *Bharat Voice OS*\nItem: {ai_analysis}\nPrice: {market_info}")
    return str(resp)

# Required for Vercel's Python Runtime
if __name__ == "__main__":
    app.run()
