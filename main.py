#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - PHIÊN BẢN HOÀN CHỈNH
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

# ====================== KHỞI TẠO BOT ======================
if __name__ == "__main__":
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    import tempfile
    import zipfile
    import requests

    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN chưa thiết lập!")
        exit(1)

    application = Application.builder().token(TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔞 Gửi lệnh `/18plus` để nhận ảnh 18+")

    async def get_18plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Đang chuẩn bị ảnh 18+...")

        # Danh sách ảnh mẫu (bạn có thể thay bằng nguồn crawl sau)
        urls = [
            "https://picsum.photos/id/1015/800/1200",
            "https://picsum.photos/id/1027/800/1200",
            "https://picsum.photos/id/106/800/1200",
            "https://picsum.photos/id/133/800/1200",
            "https://picsum.photos/id/201/800/1200",
        ]

        # Gửi từng ảnh
        for url in urls:
            try:
                await update.message.reply_photo(photo=url, caption="🔞 18+")
            except:
                await update.message.reply_text(f"Ảnh: {url}")

        # Tạo và gửi file ZIP
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, 'w') as zf:
                    for i, url in enumerate(urls):
                        try:
                            r = requests.get(url, timeout=10)
                            zf.writestr(f"18plus_{i+1}.jpg", r.content)
                        except:
                            pass
                await update.message.reply_document(
                    document=open(tmp.name, 'rb'), 
                    filename="18plus_images.zip"
                )
        except Exception as e:
            await update.message.reply_text("ZIP lỗi nhỏ, nhưng đã gửi ảnh rồi!")

    # Đăng ký lệnh
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
