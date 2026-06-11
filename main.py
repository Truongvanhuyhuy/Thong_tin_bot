#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ HOÀN CHỈNH - ĐÃ SỬA LỖI WEBHOOK 500
"""

import os
import sys
import asyncio
import logging
import threading
from io import BytesIO
import zipfile
import requests
from flask import Flask, request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Bot 18+ Dang Hoat Dong</h1><p>Online</p><a href='/health'>Health</a>"

@app.route("/health")
def health():
    return {"status": "OK", "bot": "18+", "version": "3.0"}

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    logger.error("Thieu BOT_TOKEN")
    sys.exit(1)

RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
PORT = int(os.environ.get("PORT", 8080))

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

application = (
    Application.builder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .build()
)

IMAGE_DATABASE = {
    "default": [
        "https://picsum.photos/id/1015/800/1200",
        "https://picsum.photos/id/1027/800/1200",
        "https://picsum.photos/id/106/800/1200",
        "https://picsum.photos/id/133/800/1200",
        "https://picsum.photos/id/201/800/1200",
    ],
    "gai_xinh": [
        "https://picsum.photos/id/1011/800/1200",
        "https://picsum.photos/id/1012/800/1200",
        "https://picsum.photos/id/1013/800/1200",
    ],
    "cosplay": [
        "https://picsum.photos/id/1025/800/1200",
        "https://picsum.photos/id/1026/800/1200",
    ],
}

async def download_image(url, timeout=15):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=timeout, headers=headers)
        r.raise_for_status()
        return r.content
    except:
        return None

async def send_images_batch(update, urls, caption_prefix="🔞"):
    success = 0
    fail = 0
    for idx, url in enumerate(urls, 1):
        try:
            await update.message.reply_photo(photo=url, caption=f"{caption_prefix} Anh {idx}/{len(urls)}", write_timeout=20)
            success += 1
        except:
            await update.message.reply_text(f"Link anh {idx}: {url}")
            fail += 1
    await update.message.reply_text(f"Da gui: {success} anh | Loi: {fail} anh")

async def create_zip(urls):
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, url in enumerate(urls, 1):
                img_data = await download_image(url)
                if img_data:
                    zf.writestr(f"18plus_{i:02d}.jpg", img_data)
        if zip_buffer.getbuffer().nbytes == 0:
            return None
        zip_buffer.seek(0)
        return zip_buffer
    except:
        return None

async def start_command(update, context):
    text = """
🔞 BOT 18+ DA SAN SANG

📌 Lenh:
• /18plus - Anh 18+
• /gai_xinh - Anh gai xinh
• /cosplay - Anh cosplay
• /all - Tai ZIP tong hop
• /help - Huong dan
"""
    await update.message.reply_text(text)

async def help_command(update, context):
    text = """
📚 HUONG DAN

1. Gui lenh de nhan anh
2. Moi lenh toi da 5 anh
3. Dung /all de tai ZIP
4. Neu anh loi se gui link
"""
    await update.message.reply_text(text)

async def get_18plus(update, context):
    await update.message.reply_text("Dang tai anh 18+...")
    await send_images_batch(update, IMAGE_DATABASE["default"], "🔞 18+")

async def get_gai_xinh(update, context):
    await update.message.reply_text("Dang tai anh gai xinh...")
    await send_images_batch(update, IMAGE_DATABASE["gai_xinh"], "👧 Gai Xinh")

async def get_cosplay(update, context):
    await update.message.reply_text("Dang tai anh cosplay...")
    await send_images_batch(update, IMAGE_DATABASE["cosplay"], "🎭 Cosplay")

async def get_all_zip(update, context):
    await update.message.reply_text("Dang nen ZIP... (1-2 phut)")
    all_urls = []
    for urls in IMAGE_DATABASE.values():
        all_urls.extend(urls)
    zip_data = await create_zip(all_urls)
    if zip_data:
        await update.message.reply_document(document=zip_data, filename="18plus_all.zip", caption=f"Tong hop {len(all_urls)} anh 18+", write_timeout=60)
    else:
        await update.message.reply_text("Loi tao ZIP!")

async def handle_text(update, context):
    text = update.message.text.lower()
    if any(word in text for word in ["hello", "hi", "chao"]):
        await update.message.reply_text("Chao ban! Gui /start de xem lenh!")
    elif any(word in text for word in ["anh", "ảnh"]):
        await update.message.reply_text("Gui /18plus, /gai_xinh hoac /cosplay de nhan anh!")
    else:
        await update.message.reply_text("Khong hieu lenh. Gui /help.")

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("18plus", get_18plus))
application.add_handler(CommandHandler("gai_xinh", get_gai_xinh))
application.add_handler(CommandHandler("cosplay", get_cosplay))
application.add_handler(CommandHandler("all", get_all_zip))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# =========================================================
# QUAN TRỌNG: TẠO EVENT LOOP TOÀN CỤC KHÔNG BAO GIỜ ĐÓNG
# =========================================================
main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Xử lý webhook KHÔNG async - chạy trong main_loop"""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        # Chạy async process trong main_loop an toàn
        future = asyncio.run_coroutine_threadsafe(
            application.process_update(update), 
            main_loop
        )
        future.result(timeout=30)  # Đợi xử lý xong
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return "Error", 500

def run_bot_in_thread():
    """Chạy bot trong thread riêng với event loop riêng"""
    asyncio.set_event_loop(main_loop)
    
    async def init():
        await application.initialize()
        await application.start()
        if RENDER_URL:
            webhook_url = f"{RENDER_URL}/{TOKEN}"
            try:
                await application.bot.set_webhook(webhook_url, drop_pending_updates=True, max_connections=10)
                logger.info(f"Webhook OK: {webhook_url}")
            except Exception as e:
                logger.error(f"Loi set webhook: {e}")
        else:
            logger.warning("Thieu RENDER_EXTERNAL_URL")
        logger.info("Bot da san sang!")
    
    main_loop.run_until_complete(init())
    # GIỮ EVENT LOOP MÃI MÃI - KHÔNG ĐÓNG
    main_loop.run_forever()

# Khởi động bot trong thread riêng
bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
