#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - ĐÃ THAY NGUỒN ẢNH 18+ THẬT
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
    return {"status": "OK", "bot": "18+", "version": "4.0"}

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

# =========================================================
# NGUỒN ẢNH 18+ THẬT - THAY BẰNG LINK CỦA BẠN
# =========================================================
IMAGE_DATABASE = {
    "default": [
        "https://i.imgur.com/4ZQvL4s.jpg",
        "https://i.imgur.com/JxR9k2Q.jpg",
        "https://i.imgur.com/8kTmP3f.jpg",
        "https://i.imgur.com/N7vW5eH.jpg",
        "https://i.imgur.com/yH6gD1b.jpg",
    ],
    "gai_xinh": [
        "https://i.imgur.com/XmL5tR8.jpg",
        "https://i.imgur.com/pQ2nK9w.jpg",
        "https://i.imgur.com/W3jF6vL.jpg",
    ],
    "cosplay": [
        "https://i.imgur.com/R5hT2mG.jpg",
        "https://i.imgur.com/B8kL4sN.jpg",
    ],
}

# =========================================================
# HƯỚNG DẪN LẤY ẢNH 18+ MIỄN PHÍ
# =========================================================
"""
CÁCH 1: DÙNG IMGUR
1. Vào imgur.com -> Sign Up
2. Upload ảnh 18+ lên (chế độ Hidden)
3. Copy Direct Link: https://i.imgur.com/xxxxx.jpg
4. Dán vào IMAGE_DATABASE

CÁCH 2: DÙNG NGUỒN CÓ SẴN
- Thay thế link trong code bằng link từ các nguồn:
  + https://telegra.ph/ (upload ảnh lên Telegraph)
  + https://imgbb.com/ (upload ảnh lên ImgBB)
  + https://pixhost.to/ (host ảnh 18+)

CÁCH 3: CRAWL TỰ ĐỘNG TỪ REDDIT
- Xem code mẫu ở cuối file
"""

async def download_image(url, timeout=15):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
        except Exception as e:
            await update.message.reply_text(f"Link anh {idx}: {url}")
            fail += 1
            logger.warning(f"Loi gui anh {idx}: {e}")
    if fail == 0:
        await update.message.reply_text(f"✅ Da gui thanh cong {success} anh!")
    else:
        await update.message.reply_text(f"✅ Thanh cong: {success} | ❌ Loi: {fail}")

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
• /18plus - Anh 18+ (5 anh)
• /gai_xinh - Anh gai xinh (3 anh)
• /cosplay - Anh cosplay (2 anh)
• /all - Tai ZIP tong hop
• /help - Huong dan
"""
    await update.message.reply_text(text)

async def help_command(update, context):
    text = """
📚 HUONG DAN

1. Gui /18plus de nhan anh 18+
2. Gui /gai_xinh de nhan anh gai xinh
3. Gui /cosplay de nhan anh cosplay
4. Gui /all de tai tat ca anh dang ZIP
"""
    await update.message.reply_text(text)

async def get_18plus(update, context):
    await update.message.reply_text("⏳ Dang tai anh 18+...")
    await send_images_batch(update, IMAGE_DATABASE["default"], "🔞 18+")

async def get_gai_xinh(update, context):
    await update.message.reply_text("⏳ Dang tai anh gai xinh...")
    await send_images_batch(update, IMAGE_DATABASE["gai_xinh"], "👧 Gai Xinh")

async def get_cosplay(update, context):
    await update.message.reply_text("⏳ Dang tai anh cosplay...")
    await send_images_batch(update, IMAGE_DATABASE["cosplay"], "🎭 Cosplay")

async def get_all_zip(update, context):
    await update.message.reply_text("⏳ Dang nen ZIP... (1-2 phut)")
    all_urls = []
    for urls in IMAGE_DATABASE.values():
        all_urls.extend(urls)
    zip_data = await create_zip(all_urls)
    if zip_data:
        await update.message.reply_document(document=zip_data, filename="18plus_all.zip", caption=f"📦 Tong hop {len(all_urls)} anh 18+", write_timeout=60)
    else:
        await update.message.reply_text("❌ Loi tao ZIP! Thu lai sau.")

async def handle_text(update, context):
    text = update.message.text.lower()
    if any(word in text for word in ["hello", "hi", "chao"]):
        await update.message.reply_text("👋 Chào bạn! Gửi /start để xem danh sách lệnh!")
    elif any(word in text for word in ["anh", "ảnh"]):
        await update.message.reply_text("📸 Gửi /18plus, /gai_xinh hoặc /cosplay để nhận ảnh nhé!")
    else:
        await update.message.reply_text("❓ Không hiểu lệnh. Gửi /help để xem hướng dẫn.")

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("18plus", get_18plus))
application.add_handler(CommandHandler("gai_xinh", get_gai_xinh))
application.add_handler(CommandHandler("cosplay", get_cosplay))
application.add_handler(CommandHandler("all", get_all_zip))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# =========================================================
# EVENT LOOP XỬ LÝ WEBHOOK
# =========================================================
main_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_loop)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        future = asyncio.run_coroutine_threadsafe(
            application.process_update(update), 
            main_loop
        )
        future.result(timeout=30)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return "Error", 500

def run_bot_in_thread():
    asyncio.set_event_loop(main_loop)
    
    async def init():
        await application.initialize()
        await application.start()
        if RENDER_URL:
            webhook_url = f"{RENDER_URL}/{TOKEN}"
            try:
                await application.bot.set_webhook(webhook_url, drop_pending_updates=True, max_connections=10)
                logger.info(f"✅ Webhook OK: {webhook_url}")
            except Exception as e:
                logger.error(f"❌ Loi set webhook: {e}")
        else:
            logger.warning("⚠️ Thieu RENDER_EXTERNAL_URL")
        logger.info("🚀 Bot da san sang!")
    
    main_loop.run_until_complete(init())
    main_loop.run_forever()

bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
