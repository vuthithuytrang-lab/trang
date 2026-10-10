#!/bin/bash
# Chờ cho Blogger hết chặn rồi chạy tiếp.
sleep "${1:-9000}"
cd "$(dirname "$0")" && exec python3 dang_blogger.py
