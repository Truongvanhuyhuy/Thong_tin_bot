#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM ĐA NĂNG - CHẠY 24/7
"""

import os
import tempfile
import threading
import time
import zipfile
from datetime import datetime
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ============================================
# CẤU HÌNH
# ============================================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

app = Flask(__name__)

# ============================================
# FLASK WEBHOOK
# ============================================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "🤖 Bot Telegram Đa Năng đang chạy 24/7!"

# ============================================
# KHỞI TẠO BOT
# ============================================
application = Application.builder().token(TOKEN).build()

TEMP_DIR = tempfile.gettempdir()
IMAGE_CACHE = []

# ============================================
# CRAWL ẢNH 18+
# ============================================
def crawl_18plus_images():
    global IMAGE_CACHE
    print("[18+] Đang thu thập ảnh...")
    # Code crawl đơn giản (có thể mở rộng sau)
    pass  # Hiện tại placeholder, bạn có thể thêm sau

def scheduler_18plus():
    while True:
        try:
            crawl_18plus_images()
        except:
            pass
        time.sleep(1800)

# ============================================
# TIN TỨC
# ============================================
def crawl_vietnam_news():
    sources = ["https://vnexpress.net/rss/tin-moi-nhat.rss"]
    news = []
    for url in sources:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')[:5]
            for item in items:
                title = item.find('title').text if item.find('title') else ""
                link = item.find('link').text if item.find('link') else ""
                news.append({"title": title, "link": link})
        except:
            continue
    return news

# ============================================
# THỜI TIẾT
# ============================================
def get_weather(city="Hanoi"):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=vi", timeout=10).json()
        if not geo.get("results"):
            return "Không tìm thấy thành phố."
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=Asia/Ho_Chi_Minh"
        data = requests.get(url, timeout=10).json()
        current = data["current"]
        return f"🌤️ {loc['name']}: {current['temperature_2m']}°C"
    except:
        return "Lỗi lấy thời tiết."

# ============================================
# COMMANDS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔞 Ảnh 18+", callback_data="18plus")],
        [InlineKeyboardButton("📰 Tin tức", callback_data="news")],
        [InlineKeyboardButton("🌤️ Thời tiết", callback_data="weather")],
        [InlineKeyboardButton("🌐 Dịch", callback_data="translate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 **Bot Đa Năng**\nChọn chức năng:", reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "news":
        news = crawl_vietnam_news()
        for n in news[:3]:
            await query.message.reply_text(f"📰 {n['title']}\n🔗 {n['link']}")
    elif query.data == "weather":
        await query.message.reply_text("Dùng lệnh: /weather Hà Nội")

# Đăng ký handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# ============================================
# KHỞI CHẠY
# ============================================
if __name__ == "__main__":
    threading.Thread(target=scheduler_18plus, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
