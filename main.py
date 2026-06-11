#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM ĐA NĂNG - 24/7
"""

import os
import threading
import time
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# CẤU HÌNH
# ============================================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

app = Flask(__name__)

# ============================================
# FLASK
# ============================================
@app.route("/")
def home():
    return "🤖 Bot Telegram Đa Năng đang chạy 24/7!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
    except:
        pass
    return "OK", 200

# ============================================
# KHỞI TẠO BOT
# ============================================
application = Application.builder().token(TOKEN).build()

# ============================================
# TIN TỨC
# ============================================
def crawl_news():
    try:
        r = requests.get("https://vnexpress.net/rss/tin-moi-nhat.rss", timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")[:5]
        news_list = []
        for item in items:
            title = item.find("title").text
            link = item.find("link").text
            news_list.append(f"📰 {title}\n🔗 {link}")
        return news_list
    except:
        return ["❌ Lỗi lấy tin tức."]

# ============================================
# THỜI TIẾT
# ============================================
def get_weather(city="Hà Nội"):
    try:
        # Geocoding
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=vi", timeout=8).json()
        if not geo.get("results"):
            return "Không tìm thấy thành phố."
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        
        data = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=Asia/Ho_Chi_Minh",
            timeout=8
        ).json()
        
        temp = data["current"]["temperature_2m"]
        return f"🌤️ **{loc['name']}**\nNhiệt độ: **{temp}°C**"
    except:
        return "❌ Lỗi lấy thời tiết."

# ============================================
# COMMANDS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📰 Tin tức", callback_data="news")],
        [InlineKeyboardButton("🌤️ Thời tiết", callback_data="weather")],
        [InlineKeyboardButton("🌐 Dịch", callback_data="translate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 **Bot Đa Năng**\nChọn chức năng bên dưới:", reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "news":
        news = crawl_news()
        for n in news:
            await query.message.reply_text(n)
    elif query.data == "weather":
        await query.message.reply_text("Gửi lệnh: `/weather Hà Nội`")
    elif query.data == "translate":
        await query.message.reply_text("Gửi: `/dich Xin chào` hoặc `/dich en Hello`")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "Hà Nội"
    result = get_weather(city)
    await update.message.reply_text(result)

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Cách dùng: `/dich [văn bản]` hoặc `/dich en Hello world`")
        return
    
    text = " ".join(context.args)
    try:
        translated = GoogleTranslator(source='auto', target='vi').translate(text)
        await update.message.reply_text(f"🌐 **Dịch:**\n{translated}")
    except:
        await update.message.reply_text("❌ Lỗi dịch.")

# Đăng ký handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("weather", weather_command))
application.add_handler(CommandHandler("dich", translate_command))
application.add_handler(CallbackQueryHandler(button_handler))

# ============================================
# CHẠY BOT
# ============================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print("🚀 Bot đang khởi động trên Render...")
    app.run(host="0.0.0.0", port=port)
