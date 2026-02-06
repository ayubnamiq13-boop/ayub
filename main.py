import telebot
import yfinance as yf
import google.generativeai as genai
from flask import Flask
from threading import Thread
from telebot import types

# کلیلەکانت لێرە دابنێ
TOKEN = "8424588883:AAFxOXGpsEkQjBps9eLGAh9qSWC5JS_W-HA"
GEMINI_API_KEY = "AIzaSyAtfMrX4eciLZmVZPbmtwk_8-ZcrGkSEzQ"
try:
    genai.configure(api_key=GEMINI_API_KEY)
 model = genai.GenerativeModel('gemini-2.0-flash-exp')
except:
    print("کێشە لە کلیلەکەدا هەیە")

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "سێرڤەرەکە کار دەکات!"

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('EURUSD')
    btn2 = types.KeyboardButton('GBPUSD')
    btn3 = types.KeyboardButton('BTCUSD')
    btn4 = types.KeyboardButton('GOLD (GC=F)')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 بۆتەکە ئامادەیە! دراوێک هەڵبژێرە:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def get_signal(message):
    pair = message.text.upper().replace("GOLD (GC=F)", "GC=F")
    msg = bot.reply_to(message, f"🔍 خەریکم شیکاری {pair} دەکەم...")
    
    try:
        symbol = f"{pair}=X" if len(pair) == 6 else pair
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        price = round(data['Close'].iloc[-1], 5)
        
        prompt = f"Analyze {pair} at {price}. Give me: 1. Action (BUY or SELL), 2. Duration (5m), 3. Reasoning in Kurdish."
        response = model.generate_content(prompt)
        
        bot.edit_message_text(f"📊 **{pair}**\n💰 نرخ: {price}\n\n{response.text}", message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە: {str(e)}\nتکایە دڵنیابە کلیلەکەت ڕاستە.", message.chat.id, msg.message_id)

def run():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
