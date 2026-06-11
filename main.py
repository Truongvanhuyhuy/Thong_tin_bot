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

# ====================== CẤU HÌNH ======================
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN chưa được thiết lập!")

app = Flask(__name__)

# ====================== KHỞI TẠO BOT TRƯỚC ======================
application = Application.builder().token(TOKEN).build()

# ====================== FLASK ======================
@app.route("/")
def home():
    return "🤖 Bot Telegram Đa Năng đang chạy 24/7!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
    except Exception as e:
        print(f"Webhook error: {e}")
    return "OK", 200

# ====================== CÁC HÀM HỖ TRỢ ======================
def crawl_news():
    try:
        r = requests.get("https://vnexpress.net/rss/tin-moi-nhat.rss", timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")[:5]
        return [f"📰 {item.find('title').text}\n🔗 {item.find('link').text}" for item in items]
    except:
        return ["❌ Không lấy được tin tức."]

def get_weather(city="Hà Nội"):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=vi", timeout=8).json()
        if not geo.get("results"):
            return "Không tìm thấy thành phố."
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        data = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=Asia/Ho_Chi_Minh",
            timeout=8
        ).json()
        temp = data["current"]["temperature_2m"]
        return f"🌤️ **{loc['name']}
