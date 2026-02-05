import telebot
import yfinance as yf
import google.generativeai as genai

# ١. کلیلەکانی خۆت لێرە دابنێ
TOKEN = "8424588883:AAFxOXGpsEkQjBps9eLGAh9qSWC5JS_W-HA"
GEMINI_API_KEY = "AIzaSy..."


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def get_signal(message):
    pair = message.text.upper().replace("/", "")
    bot.send_message(message.chat.id, f"🔍 خەریکم شیکاری {pair} دەکەم بۆ Pocket Option...")
    
    try:
        # وەرگرتنی داتا بۆ ٥ خولەک
        symbol = f"{pair}=X" if len(pair) == 6 else pair
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        price = data['Close'].iloc[-1]
        
        prompt = f"وەک پسپۆڕی پۆکێت ئۆپشن، نرخی {pair} ئێستا {price}ـە. بە کورتی بڵێ Call یان Put بۆ ٥ خولەک؟"
        response = model.generate_content(prompt)
        
        bot.reply_to(message, f"🎯 پێشنیاری AI:\n\n💰 نرخ: {price}\n💡 بڕیار: {response.text}")
    except:
        bot.reply_to(message, "ناوی دراوەکە بە ڕاستی بنووسە، وەک: EURUSD")
        flask

print("بۆتەکە چالاکە...")
bot.infinity_polling()
