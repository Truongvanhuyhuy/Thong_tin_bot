#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - PHIÊN BẢN ỔN ĐỊNH
"""

import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN chưa được thiết lập!")

app = Flask(__name__)

# Khởi tạo Application
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "🤖 Bot 18+ Đang chạy!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

# ====================== CHỨC NĂNG 18+ ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔞 Gửi lệnh /18plus để nhận ảnh 18+")

async def get_18plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Đang gửi ảnh 18+... (hiện dùng link mẫu)")

    # Gửi vài ảnh mẫu
    urls = [
        "https://picsum.photos/id/1015/800/1200",
        "https://picsum.photos/id/1027/800/1200",
        "https://picsum.photos/id/106/800/1200",
    ]
    for url in urls:
        try:
            await update.message.reply_photo(photo=url, caption="🔞 18+")
        except:
            await update.message.reply_text(f"Ảnh: {url}")

# Đăng ký lệnh
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("18plus", get_18plus))

# ====================== CHẠY ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("🚀 Bot 18+ khởi động...")
    app.run(host="0.0.0.0", port=port)
