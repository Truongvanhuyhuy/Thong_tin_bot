#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM ĐA NĂNG - CHẠY 24/7 TRÊN RENDER.COM
Tích hợp: Ảnh 18+, Tin tức VN, Thời tiết, Dịch thuật
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
TOKEN = os.environ.get("BOT_TOKEN")          # ← Đặt trong Render Environment Variables
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
    sources = [
        "https://www.reddit.com/r/nsfw.json?limit=30",
        "https://www.reddit.com/r/RealGirls.json?limit=20",
        "https://www.reddit.com/r/amateur.json?limit=20",
    ]
    
    all_images = []
    for source in sources:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(source, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    post_data = post.get("data", {})
                    url = post_data.get("url", "")
                    title = post_data.get("title", "NSFW")[:50]
                    if url and any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        all_images.append({"title": title, "url": url})
        except:
            continue
    
    if len(all_images) >= 5:
        zip_name = f"18plus_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
        zip_path = os.path.join(TEMP_DIR, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            count = 0
            for img in all_images[:25]:
                try:
                    img_data = requests.get(img['url'], timeout=10)
                    if img_data.status_code == 200:
                        ext = img['url'].split('.')[-1].split('?')[0]
                        filename = f"{img['title'][:30]}_{count}.{ext}"
                        zf.writestr(filename, img_data.content)
                        count += 1
                except:
                    continue
        
        IMAGE_CACHE.append({
            "path": zip_path,
            "name": zip_name,
            "count": count,
            "time": datetime.now()
        })
        
        if len(IMAGE_CACHE) > 8:
            old = IMAGE_CACHE.pop(0)
            try:
                os.remove(old['path'])
            except:
                pass

def scheduler_18plus():
    while True:
        try:
            crawl_18plus_images()
        except:
            pass
        time.sleep(1800)  # 30 phút

# ============================================
# TIN TỨC VIỆT NAM
# ============================================
def crawl_vietnam_news():
    sources = [
        "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "https://tuoitre.vn/rss/tin-moi-nhat.rss",
        "https://vietnamnet.vn/rss/thoi-su.rss"
    ]
    news = []
    for url in sources:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')[:4]
            for item in items:
                title = item.find('title').text if item.find('title') else ""
                link = item.find('link').text if item.find('link') else ""
                desc = item.find('description').text if item.find('description') else ""
                news.append({"title": title, "link": link, "desc": desc[:150]})
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
            return None
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=Asia/Ho_Chi_Minh"
        data = requests.get(url, timeout=10).json()
        current = data["current"]
        
        weather_codes = {0:"Quang đãng", 1:"Ít mây", 2:"Có mây", 3:"Nhiều mây", 45:"Sương mù", 61:"Mưa nhẹ", 63:"Mưa vừa", 80:"Mưa rào"}
        code = current.get("weather_code", 0)
        
        return f"🌤️ **{loc['name']}, {loc.get('country','')}**\n🌡️ Nhiệt độ: {current['temperature_2m']}°C\n⛅ {weather_codes.get(code, 'Không xác định')}"
    except:
        return None

# ============================================
# COMMANDS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔞 Ảnh 18+", callback_data="18plus")],
        [InlineKeyboardButton("📰 Tin tức VN", callback_data="news")],
        [InlineKeyboardButton("🌤️ Thời tiết", callback_data="weather")],
        [InlineKeyboardButton("🌐 Dịch văn bản", callback_data="translate")],
        [InlineKeyboardButton("ℹ️ Hướng dẫn", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **BOT ĐA NĂNG 24/7**\n\nChọn chức năng bên dưới:", 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "18plus":
        await get_18plus(update, context)
    elif query.data == "news":
        await get_news(update, context)
    elif query.data == "weather":
        await query.message.reply_text("Dùng lệnh: /weather Hà Nội")
    elif query.data == "translate":
        await query.message.reply_text("Dùng: /dich en Xin chào")
    elif query.data == "help":
        await help_command(update, context)

async def get_18plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not IMAGE_CACHE:
        await update.message.reply_text("Đang thu thập ảnh 18+... Vui lòng chờ 10-20 giây")
        crawl_18plus_images()
        time.sleep(8)
    
    if IMAGE_CACHE:
        latest = IMAGE_CACHE[-1]
        with open(latest['path'], 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=latest['name'],
                caption=f"🔞 {latest['name']}\n📦 {latest['count']} ảnh"
            )
    else:
        await update.message.reply_text("Chưa có ảnh. Thử lại sau!")

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📰 Đang tải tin tức...")
    news = crawl_vietnam_news()
    for item in news[:5]:
        text = f"**{item['title']}**\n{item['desc']}...\n🔗 [Đọc tiếp]({item['link']})"
        await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
        time.sleep(0.6)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = ' '.join(context.args) if context.args else "Hanoi"
    await update.message.reply_text(f"🌤️ Đang tra cứu {city}...")
    report = get_weather(city)
    await update.message.reply_text(report or "Không tìm thấy thời tiết.")

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Cách dùng: /dich en Xin chào")
        return
    target = context.args[0]
    text = ' '.join(context.args[1:])
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        await update.message.reply_text(f"🌐 **Dịch sang {target}:**\n{translated}")
    except:
        await update.message.reply_text("Lỗi dịch thuật.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 **HƯỚNG DẪN**
/start - Menu chính
/18plus - Ảnh 18+ ZIP
/news - Tin tức VN
/weather Hà Nội - Thời tiết
/dich en Xin chào - Dịch
"""
    await update.message.reply_text(text)

# ============================================
# ĐĂNG KÝ HANDLERS
# ============================================
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("18plus", get_18plus))
application.add_handler(CommandHandler("news", get_news))
application.add_handler(CommandHandler("weather", weather_command))
application.add_handler(CommandHandler("dich", translate_command))
application.add_handler(CallbackQueryHandler(button_handler))

# ============================================
# KHỞI CHẠY
# ============================================
if __name__ == "__main__":
    threading.Thread(target=scheduler_18plus, daemon=True).start()
    
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Bot đang chạy trên port {port}")
    app.run(host="0.0.0.0", port=port)