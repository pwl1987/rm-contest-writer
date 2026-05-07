#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DEPRECATED - 使用 .js 版本
# 保留至 Phase 2 完成验证
"""
前置依赖检查与安装脚本
检查并安装：playwright、chromium、python-docx（venv）
"""

import os
import sys
import json
import subprocess
import shutil
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = '/tmp/docconvert-venv/bin/python3'
VENV_PIP = '/tmp/docconvert-venv/bin/pip'
PLAYWRIGHT_PYTHON = '/tmp/docconvert-venv/bin/python3'
CHROMIUM_PATH = '/tmp/chrome-linux/chrome'


def log(msg):
    print(f'[preflight] {msg}')


def warn(msg):
    print(f'[preflight WARN] {msg}')


def error(msg):
    print(f'[preflight ERROR] {msg}')


def run_sync(cmd, args=None, env=None, cwd=None, timeout=60):
    try:
        kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': timeout,
        }
        if env:
            kwargs['env'] = env
        if cwd:
            kwargs['cwd'] = cwd
        result = subprocess.run(
            [cmd] + (args or []),
            **kwargs
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, Exception) as e:
        return None


def check_playwright():
    log('检查 playwright...')
    # 优先检查 npm playwright（已安装在 word-gen/node_modules）
    playwright_nm = os.path.join(ROOT, 'word-gen', 'node_modules', 'playwright', 'package.json')
    if os.path.exists(playwright_nm):
        log('playwright (npm) 已安装 ✅')
        # 同时检查 Python playwright 是否可用
        try:
            out = run_sync(VENV_PYTHON, ['-c', 'from playwright.sync_api import sync_playwright; print("ok")'])
            if out and 'ok' in out:
                log('playwright (Python venv) 已安装 ✅')
        except:
            pass
        return True

    log('安装 playwright (npm)...')
    try:
        subprocess.run(
            ['npm', 'install', 'playwright'],
            capture_output=True, timeout=120,
            cwd=os.path.join(ROOT, 'word-gen')
        )
        log('playwright (npm) 安装成功 ✅')
        return True
    except Exception as e:
        warn(f'playwright 安装失败: {e}')
        return False


def check_chromium():
    log('检查 chromium...')
    if os.path.exists(CHROMIUM_PATH):
        log('chromium 已安装 ✅')
        return True

    log('安装 chromium（通过 socks5 代理下载）...')
    try:
        socks_proxy = 'socks5://10.30.5.62:1081'
        revision = '1625362'
        base_url = f'https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/{revision}'
        url = f'{base_url}/chrome-linux.zip'
        zip_path = '/tmp/chrome-linux.zip'

        log(f'下载: {url}')
        # 使用 urllib 通过 socks5 代理下载
        import urllib.request

        proxy_handler = urllib.request.ProxyHandler({
            'http': socks_proxy,
            'https': socks_proxy,
        })
        opener = urllib.request.build_opener(proxy_handler)

        def download_progress(count, block_size, total_size):
            if total_size > 0 and count % 500 == 0:
                pct = int(count * block_size * 100 / total_size)
                log(f'下载进度: {pct}%')

        urllib.request.urlretrieve(url, zip_path, download_progress)
        log('下载完成，正在解压...')
        subprocess.run(['unzip', '-q', '-o', '/tmp/chrome-linux.zip', '-d', '/tmp'],
                       capture_output=True, timeout=120)
        if os.path.exists(CHROMIUM_PATH):
            log('chromium 安装成功 ✅')
            return True
    except Exception as e:
        warn(f'chromium 安装失败: {e}')

    return False


def check_python_docx():
    log('检查 python-docx (venv)...')
    try:
        if os.path.exists(VENV_PYTHON):
            out = run_sync(VENV_PYTHON, ['-c', 'from docx import Document; print("ok")'])
            if out and 'ok' in out:
                log('python-docx 已安装 ✅')
                return True
    except Exception:
        pass

    log('设置 python-docx venv...')
    try:
        if not os.path.exists('/tmp/docconvert-venv'):
            subprocess.run([sys.executable, '-m', 'venv', '/tmp/docconvert-venv'],
                          capture_output=True, timeout=60)
        env = os.environ.copy()
        for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
            env.pop(k, None)
        subprocess.run([VENV_PIP, 'install', 'python-docx', '--no-proxy'],
                       capture_output=True, timeout=120, env=env)
        log('python-docx 安装成功 ✅')
        return True
    except Exception as e:
        warn(f'python-docx 安装失败: {e}')
        return False


def main():
    log('========== 前置依赖检查 ==========')
    log('')

    results = {
        'playwright': check_playwright(),
        'chromium': check_chromium(),
        'pythonDocx': check_python_docx(),
    }

    log('')
    log('========== 检查结果汇总 ==========')
    all_ok = all(results.values())
    if all_ok:
        log('所有依赖检查通过 ✅')
    else:
        failed = [k for k, v in results.items() if not v]
        warn(f'部分依赖缺失（将使用 fallback）：{", ".join(failed)}')

    status_file = '/tmp/preflight-status.json'
    with open(status_file, 'w') as f:
        json.dump({**results, 'allOk': all_ok}, f, indent=2)
    log(f'状态已写入 {status_file}')

    sys.exit(0)


if __name__ == '__main__':
    main()