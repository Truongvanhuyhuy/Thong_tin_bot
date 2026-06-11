#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM ĐA NĂNG - 24/7
"""

import os
from flask import Flask

# ============================================
# FLASK APP
# ============================================
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot đang chạy! Kiểm tra webhook."

@app.route("/health")
def health():
    return "OK"

# ============================================
# KHỞI ĐỘNG BOT (chỉ khi chạy trực tiếp)
# ============================================
if __name__ == "__main__":
    print("🚀 Bot khởi động...")
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ LỖI: BOT_TOKEN chưa được thiết lập!")
        exit(1)
    
    print(f"✅ Token đã load: {TOKEN[:10]}...")
    # Code bot đầy đủ sẽ được thêm sau khi fix crash
    print("Bot sẵn sàng!")
