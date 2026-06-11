#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT 18+ - SIÊU TỐI GIẢN
"""

import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot 18+ Test - Đang chạy!"

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("🚀 Bot 18+ Test khởi động...")
    app.run(host="0.0.0.0", port=port)
