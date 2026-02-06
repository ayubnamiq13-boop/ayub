import telebot
import yfinance as yf
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
# ١. کلیلەکان لێرە دابنێ
TOKEN = "8424588883:AAFxOXGpsEkQjBps9eLGAh9qSWC5JS_W-HA"
GEMINI_API_KEY = "gen-lang-client-0913413375"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "بۆتەکە چالاکە!"

@bot.message_handler(func=lambda message: True)
def get_signal(message):
    pair = message.text.upper().replace("/", "")
    bot.send_message(message.chat.id, f"🔍 خەریکم شیکاری {pair} دەکەم بۆ Pocket Option...")
    try:
        symbol = f"{pair}=X" if len(pair) == 6 else pair
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        price = data['Close'].iloc[-1]
        prompt = f"بە کورتی بڵێ بۆ ٥ خولەک Call یان Put بکەم؟ نرخ ئێستا {price}ـە بۆ {pair}. وەک پسپۆڕی باکێت ئۆپشن نرخەکە بزانە."
        response = model.generate_content(prompt)
        bot.reply_to(message, f"🎯 پێشنیاری AI:\n\n💰 نرخ: {price}\n{response.text}")
def run():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
