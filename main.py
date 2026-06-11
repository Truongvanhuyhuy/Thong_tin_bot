#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TEST - SIÊU ĐƠN GIẢN
"""

import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
application = Application.builder().token(TOKEN).build()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Test Đang Chạy!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
    except:
        pass
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot đang hoạt động!\nGõ /test để kiểm tra.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Bot trả lời bình thường!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("test", test))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
