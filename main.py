#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - PHIÊN BẢN CUỐI CÙNG
"""

import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot 18+ Đang chạy trên Render!"

@app.route("/health")
def health():
    return "OK"

# ====================== CHỈ KHỞI TẠO KHI CHẠY THẬT ======================
if __name__ == "__main__":
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN chưa thiết lập!")
        exit(1)

    application = Application.builder().token(TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔞 Gửi /18plus để nhận ảnh")

    async def get_18plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Đang gửi ảnh 18+...")

        urls = [
            "https://picsum.photos/id/1015/800/1200",
            "https://picsum.photos/id/1027/800/1200",
            "https://picsum.photos/id/106/800/1200",
            "https://picsum.photos/id/133/800/1200",
        ]
        for url in urls:
            try:
                await update.message.reply_photo(photo=url, caption="🔞 18+")
            except:
                await update.message.reply_text(url)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("18plus", get_18plus))

    # Webhook
    @app.route(f"/{TOKEN}", methods=["POST"])
    def webhook():
        try:
            update = Update.de_json(request.get_json(force=True), application.bot)
            application.process_update(update)
        except:
            pass
        return "OK", 200

    port = int(os.environ.get("PORT", 8080))
    print("🚀 Bot 18+ khởi động...")
    app.run(host="0.0.0.0", port=port)
