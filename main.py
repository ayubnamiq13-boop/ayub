import telebot
import yfinance as yf
import google.generativeai as genai
from flask import Flask
from threading import Thread
from telebot import types

# کلیلەکانت
TOKEN = "8424588883:AAFxOXGpsEkQjBps9eLGAh9qSWC5JS_W-HA"
GEMINI_API_KEY = "AIzaSyAtfMrX4eciLZmVZPbmtwk_8-ZcrGkSEzQ"

# ڕێکخستنی مۆدێل (لێرەدا وەشانی نوێمان داناوە بۆ چارەسەری هەڵەی 404)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
    msg = bot.reply_to(message, f"🔍 خەریکم شیکاری {pair} دەکەم بۆ Pocket Option...")
    
    try:
        # وەرگرتنی داتا لە Yahoo Finance
        symbol = f"{pair}=X" if len(pair) == 6 else pair
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        
        if data.empty:
            bot.edit_message_text("❌ داتای بازاڕ نەدۆزرایەوە.", message.chat.id, msg.message_id)
            return

        price = round(data['Close'].iloc[-1], 5)
        
        # ناردنی داواکاری بۆ Gemini
        prompt = f"Analyze the candlestick chart for {pair} at price {price}. Tell me to BUY or SELL for a 5-minute duration and give a short reason in Kurdish."
        response = model.generate_content(prompt)
        
        final_text = f"📊 **{pair}**\n💰 نرخ: {price}\n\n{response.text}"
        bot.edit_message_text(final_text, message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"⚠️ هەڵەیەک ڕوویدا: {str(e)}\nدڵنیابە API Key ڕاستە.", message.chat.id, msg.message_id)

def run():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
