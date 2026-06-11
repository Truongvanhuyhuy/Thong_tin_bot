#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - TỰ ĐỘNG LẤY ẢNH TỪ GOOGLE & REDDIT
"""

import os
import sys
import asyncio
import logging
import threading
import random
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
    return "<h1>Bot 18+ Dang Hoat Dong</h1><p>Online - Auto Crawl</p><a href='/health'>Health</a>"

@app.route("/health")
def health():
    return {"status": "OK", "bot": "18+", "version": "5.0", "mode": "auto_crawl"}

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
# HÀM TỰ ĐỘNG CRAWL ẢNH TỪ NHIỀU NGUỒN
# =========================================================

def crawl_reddit(subreddit="nsfw", limit=10):
    """Lấy ảnh từ Reddit qua JSON API (không cần API key)"""
    urls = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        for post in data["data"]["children"]:
            post_data = post["data"]
            img_url = post_data.get("url", "")
            # Lọc chỉ lấy ảnh (jpg, png, gif) từ i.redd.it hoặc imgur
            if any(ext in img_url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                if "i.redd.it" in img_url or "i.imgur.com" in img_url:
                    urls.append(img_url)
        logger.info(f"Crawl Reddit r/{subreddit}: Tim thay {len(urls)} anh")
    except Exception as e:
        logger.warning(f"Loi crawl Reddit: {e}")
    return urls

def crawl_google(query="nsfw", limit=10):
    """Lấy ảnh từ Google Images (dùng SerpAPI hoặc scrape cơ bản)"""
    urls = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        # Dùng Google Custom Search API miễn phí (100 queries/ngày)
        # Hoặc dùng trang proxy: unsplash.com, pexels.com
        search_url = f"https://www.google.com/search?q={query}&tbm=isch&hl=en"
        r = requests.get(search_url, headers=headers, timeout=10)
        
        # Parse HTML để lấy link ảnh (cách đơn giản)
        import re
        # Tìm tất cả URL ảnh trong kết quả Google
        img_urls = re.findall(r'"ou":"(https?://[^"]+\.(?:jpg|jpeg|png|gif))"', r.text)
        urls = img_urls[:limit]
        logger.info(f"Crawl Google '{query}': Tim thay {len(urls)} anh")
    except Exception as e:
        logger.warning(f"Loi crawl Google: {e}")
    return urls

def crawl_picsum():
    """Dùng Picsum ảnh stock (tạm thời nếu các nguồn khác lỗi)"""
    # Tạo URL ảnh ngẫu nhiên từ Picsum
    urls = []
    for i in range(5):
        # Dùng seed cố định để có ảnh nhất quán
        seed = random.randint(1, 1000)
        urls.append(f"https://picsum.photos/seed/{seed}/800/1200")
    return urls

# Cache ảnh để khỏi crawl liên tục
IMAGE_CACHE = {
    "default": [],
    "gai_xinh": [],
    "cosplay": [],
}

def refresh_cache():
    """Làm mới cache ảnh từ các nguồn"""
    logger.info("Dang crawl anh moi...")
    
    # Crawl từ Reddit
    nsfw_images = crawl_reddit("nsfw", 10)
    if nsfw_images:
        IMAGE_CACHE["default"] = nsfw_images
    
    # Crawl thêm từ subreddit khác
    gai_xinh = crawl_reddit("AsianHotties", 5)
    if gai_xinh:
        IMAGE_CACHE["gai_xinh"] = gai_xinh
    
    cosplay = crawl_reddit("cosplaygirls", 5)
    if cosplay:
        IMAGE_CACHE["cosplay"] = cosplay
    
    # Nếu Reddit không có, crawl từ Google
    if not IMAGE_CACHE["default"]:
        IMAGE_CACHE["default"] = crawl_google("nsfw 18+", 5)
    if not IMAGE_CACHE["gai_xinh"]:
        IMAGE_CACHE["gai_xinh"] = crawl_google("gái xinh", 5)
    if not IMAGE_CACHE["cosplay"]:
        IMAGE_CACHE["cosplay"] = crawl_google("cosplay sexy", 5)
    
    # Nếu vẫn không có, dùng ảnh stock
    if not IMAGE_CACHE["default"]:
        IMAGE_CACHE["default"] = crawl_picsum()
    
    logger.info(f"Cache: default={len(IMAGE_CACHE['default'])}, gai_xinh={len(IMAGE_CACHE['gai_xinh'])}, cosplay={len(IMAGE_CACHE['cosplay'])}")

def get_random_images(category="default", count=5):
    """Lấy ảnh ngẫu nhiên từ cache"""
    if not IMAGE_CACHE.get(category):
        refresh_cache()
    
    images = IMAGE_CACHE.get(category, [])
    if not images:
        images = crawl_picsum()
    
    # Trả về tối đa 'count' ảnh ngẫu nhiên
    if len(images) > count:
        return random.sample(images, count)
    return images

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
            await update.message.reply_text(f"🔗 Link anh {idx}: {url}")
            fail += 1
    if fail == 0:
        await update.message.reply_text(f"✅ Da gui {success} anh thanh cong!")
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
🔞 BOT 18+ AUTO CRAWL

📌 Lenh:
• /18plus - Anh 18+ tu dong (5 anh)
• /gai_xinh - Anh gai xinh (3 anh)  
• /cosplay - Anh cosplay (2 anh)
• /all - Tai ZIP tong hop
• /refresh - Crawl anh moi ngay
• /help - Huong dan
"""
    await update.message.reply_text(text)

async def help_command(update, context):
    text = """
📚 HUONG DAN

🚀 Anh duoc crawl tu dong tu:
• Reddit: r/nsfw, r/AsianHotties
• Google Images
• Picsum (fallback)

🔄 Gui /refresh de crawl anh moi
📦 Gui /all de tai ZIP
"""
    await update.message.reply_text(text)

async def refresh_command(update, context):
    """Lệnh refresh - crawl ảnh mới"""
    await update.message.reply_text("⏳ Dang crawl anh moi tu Reddit & Google...")
    refresh_cache()
    await update.message.reply_text(f"✅ Da crawl xong!\n📊 Default: {len(IMAGE_CACHE['default'])} anh\n📊 Gai Xinh: {len(IMAGE_CACHE['gai_xinh'])} anh\n📊 Cosplay: {len(IMAGE_CACHE['cosplay'])} anh")

async def get_18plus(update, context):
    await update.message.reply_text("⏳ Dang lay anh 18+...")
    urls = get_random_images("default", 5)
    await send_images_batch(update, urls, "🔞 18+")

async def get_gai_xinh(update, context):
    await update.message.reply_text("⏳ Dang lay anh gai xinh...")
    urls = get_random_images("gai_xinh", 3)
    await send_images_batch(update, urls, "👧 Gai Xinh")

async def get_cosplay(update, context):
    await update.message.reply_text("⏳ Dang lay anh cosplay...")
    urls = get_random_images("cosplay", 2)
    await send_images_batch(update, urls, "🎭 Cosplay")

async def get_all_zip(update, context):
    await update.message.reply_text("⏳ Dang nen ZIP... (1-2 phut)")
    all_urls = []
    all_urls.extend(get_random_images("default", 5))
    all_urls.extend(get_random_images("gai_xinh", 3))
    all_urls.extend(get_random_images("cosplay", 2))
    zip_data = await create_zip(all_urls)
    if zip_data:
        await update.message.reply_document(document=zip_data, filename="18plus_all.zip", caption=f"📦 Tong hop {len(all_urls)} anh 18+", write_timeout=60)
    else:
        await update.message.reply_text("❌ Loi tao ZIP!")

async def handle_text(update, context):
    text = update.message.text.lower()
    if any(word in text for word in ["hello", "hi", "chao"]):
        await update.message.reply_text("👋 Chào bạn! Gửi /start để xem lệnh!")
    elif any(word in text for word in ["anh", "ảnh"]):
        await update.message.reply_text("📸 Gửi /18plus, /gai_xinh hoặc /cosplay!")
    else:
        await update.message.reply_text("❓ Gửi /help để xem hướng dẫn.")

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("refresh", refresh_command))
application.add_handler(CommandHandler("18plus", get_18plus))
application.add_handler(CommandHandler("gai_xinh", get_gai_xinh))
application.add_handler(CommandHandler("cosplay", get_cosplay))
application.add_handler(CommandHandler("all", get_all_zip))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# =========================================================
# EVENT LOOP
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
        # Crawl ảnh lần đầu
        refresh_cache()
        if RENDER_URL:
            webhook_url = f"{RENDER_URL}/{TOKEN}"
            try:
                await application.bot.set_webhook(webhook_url, drop_pending_updates=True, max_connections=10)
                logger.info(f"✅ Webhook OK: {webhook_url}")
            except Exception as e:
                logger.error(f"❌ Loi set webhook: {e}")
        logger.info("🚀 Bot Auto Crawl da san sang!")
    
    main_loop.run_until_complete(init())
    main_loop.run_forever()

bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
