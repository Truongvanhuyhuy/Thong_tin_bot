#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - PHIÊN BẢN TEST
"""

import os
import tempfile
import zipfile
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN chưa được thiết lập!")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "🤖 Bot 18+ Test đang chạy!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
    except:
        pass
    return "OK", 200

# Danh sách link ảnh 18+ mẫu (có thể thay bằng nguồn crawl sau)
IMAGE_URLS = [
    "https://picsum.photos/id/1015/800/600",  # Thay bằng link thật sau
    "https://picsum.photos/id/1027/800/600",
    "https://picsum.photos/id/106/800/600",
    "https://picsum.photos/id/133/800/600",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔞 **Bot 18+ Test**\nGửi lệnh /18plus để nhận ảnh.")

async def get_18plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Đang chuẩn bị gói ảnh 18+...")
    
    # Gửi vài ảnh trực tiếp
    for url in IMAGE_URLS[:4]:
        try:
            await update.message.reply_photo(photo=url)
        except:
            await update.message.reply_text(f"Ảnh: {url}")
    
    # Tạo file ZIP
    try:
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            with zipfile.ZipFile(tmp.name, 'w') as zf:
                for i, url in enumerate(IMAGE_URLS):
                    try:
                        r = requests.get(url, timeout=10)
                        zf.writestr(f"image_{i+1}.jpg", r.content)
                    except:
                        pass
            await update.message.reply_document(document=open(tmp.name, 'rb'), filename="18plus_images.zip")
    except:
        await update.message.reply_text("✅ Đã gửi ảnh. ZIP lỗi nhỏ.")

# Đăng ký lệnh
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("18plus", get_18plus))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("🚀 Bot 18+ Test khởi động...")
    app.run(host="0.0.0.0", port=port)
