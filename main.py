#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM ĐA NĂNG - PHIÊN BẢN HOẠT ĐỘNG TRÊN RENDER
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot Telegram Đa Năng đang chạy 24/7 trên Render.com!"

@app.route("/health")
def health():
    return "OK"

# ============================================
# KHỞI ĐỘNG BOT (chỉ khi chạy trực tiếp)
# ============================================
if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ LỖI: Chưa thiết lập BOT_TOKEN trong Environment Variables!")
        exit(1)
    
    print("✅ Bot khởi động thành công!")
    print(f"Token: {TOKEN[:15]}...")
    
    # Code đầy đủ sẽ được thêm sau khi fix lỗi cơ bản
    print("Bot đang chạy...")
