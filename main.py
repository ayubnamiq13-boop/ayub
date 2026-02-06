import telebot
import yfinance as yf
import google.generativeai as genai
from flask import Flask
from threading import Thread
from telebot import types


TOKEN = "8424588883:AAFxOXGpsEkQjBps9eLGAh9qSWC5JS_W-HA"
GEMINI_API_KEY = "AIzaSyAtfMrX4eciLZmVZPbmtwk_8-ZcrGkSEzQ"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "بۆتەکە چالاکە!"

# مینیۆی دوگمەکان
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
    bot.reply_to(message, "سڵاو! یەکێک لەم دراوانە هەڵبژێرە بۆ وەرگرتنی سیگناڵ:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def get_signal(message):
    pair = message.text.upper().replace("GOLD (GC=F)", "GC=F")
    msg = bot.send_message(message.chat.id, f"🔍 خەریکم شیکاری {pair} دەكەم...")
    
    try:
        symbol = f"{pair}=X" if len(pair) == 6 else pair
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        price = round(data['Close'].iloc[-1], 5)
        
        # ناردنی زانیاری بۆ Gemini بۆ بڕیاردان
        prompt = f"Act as a professional binary options trader. Analyze {pair} at price {price}. Give me a signal: 1. Action (BUY or SELL in bold), 2. Duration (in minutes), 3. Confidence level (%). Keep it very short in Kurdish."
        
        response = model.generate_content(prompt)
        
        # دیاریکردنی ڕەنگ یان ئیمۆجی بەپێی وەڵامەکە
        signal_text = response.text
        emoji = "🟢" if "BUY" in signal_text.upper() or "CALL" in signal_text.upper() else "🔴"
        
        final_message = (
            f"📊 **Symbol:** {pair}\n"
            f"💰 **Price:** {price}\n"
            f"━━━━━━━━━━━━━━\n"
            f"{emoji} **Signal:** {signal_text}\n"
            f"━━━━━━━━━━━━━━\n"
            f"⏰ **Timeframe:** 5 Minutes"
        )
        
        bot.edit_message_text(final_message, message.chat.id, msg.message_id, parse_mode="Markdown")
        
    except Exception as e:
        bot.edit_message_text("⚠️ هەڵەیەک ڕوویدا. دڵنیابە API Key ڕاستە.", message.chat.id, msg.message_id)

def run():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
