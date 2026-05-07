#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DEPRECATED - 使用 .js 版本
# 保留至 Phase 2 完成验证
"""
使用 Playwright 无头模式截图架构图 HTML
优先使用 Node.js（稳定），Python playwright 作为备用

用法: python3 capture-diagram.py <html文件路径> <输出png路径>
"""

import sys
import os
import subprocess
import http.server
import socketserver
import threading
import shutil

HTML_PATH = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_PNG = sys.argv[2] if len(sys.argv) > 2 else None

if not HTML_PATH or not OUTPUT_PNG:
    print('用法: python3 capture-diagram.py <html文件路径> <输出png路径>')
    sys.exit(1)

CHROMIUM_PATH = '/tmp/chrome-linux/chrome'
HTTP_PORT = 8899


def check_playwright_python():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        super().do_GET()


def start_http_server(dir_path, port):
    os.chdir(dir_path)
    with socketserver.TCPServer(('', port), QuietHandler) as httpd:
        httpd.serve_forever()


def capture_with_node(html_path, output_png):
    """主要方案：使用 Node.js + playwright"""
    script = '/home/lytv/.claude/skills/rm-contest-writer/word-gen/capture-diagram.js'
    try:
        result = subprocess.run(
            ['node', script, html_path, output_png],
            capture_output=True, text=True, timeout=90
        )
        if result.returncode == 0 and os.path.exists(output_png):
            size = os.stat(output_png).st_size
            print(f'截图已保存（Node.js）: {output_png} ({size} bytes)')
            return True
        else:
            print(f'Node.js capture failed: {result.stderr[:200] if result.stderr else "unknown error"}')
            return False
    except subprocess.TimeoutExpired:
        print('Node.js capture 超时（90s），使用备用方案')
        return False
    except Exception as e:
        print(f'Node.js capture error: {e}')
        return False


def capture_with_python(html_path, output_png):
    """备用方案：Python playwright"""
    print('使用 Python playwright...')
    html_abs = os.path.abspath(html_path)
    dir_path = os.path.dirname(html_abs)
    html_name = os.path.basename(html_abs)

    server_thread = threading.Thread(
        target=start_http_server, args=(dir_path, HTTP_PORT), daemon=True
    )
    server_thread.start()
    server_thread.join(timeout=1)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        page.set_viewport_size({'width': 1280, 'height': 960})
        target_url = f'http://localhost:{HTTP_PORT}/{html_name}'
        page.goto(target_url, wait_until='domcontentloaded', timeout=15000)
        page.wait_for_timeout(2000)
        page.screenshot(path=output_png, type='png', full_page=True)
        browser.close()
    size = os.stat(output_png).st_size
    print(f'截图已保存（Python）: {output_png} ({size} bytes)')
    return True


def capture_diagram():
    # 优先 Node.js（稳定可靠）
    if capture_with_node(HTML_PATH, OUTPUT_PNG):
        return

    # 备用 Python playwright
    if check_playwright_python():
        if capture_with_python(HTML_PATH, OUTPUT_PNG):
            return

    # 最终备用：复制同名 PNG（如果存在）
    dir_path = os.path.dirname(os.path.abspath(HTML_PATH))
    png_from_md = os.path.join(dir_path, os.path.basename(HTML_PATH).replace('.html', '.png'))
    if os.path.exists(png_from_md):
        shutil.copy2(png_from_md, OUTPUT_PNG)
        size = os.stat(OUTPUT_PNG).st_size
        print(f'已复制已有 PNG: {png_from_md} → {OUTPUT_PNG} ({size} bytes)')
        return

    print(f'截图失败：无法捕获 {HTML_PATH}')
    sys.exit(1)


if __name__ == '__main__':
    capture_diagram()