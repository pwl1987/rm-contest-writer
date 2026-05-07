#!/usr/bin/env node
/**
 * 前置依赖检查与安装脚本
 * 检查并安装：playwright、chromium、python-docx
 * 用法：node preflight-check.js
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = '/home/lytv/.claude/skills/rm-contest-writer';
const VENV_PYTHON = '/tmp/docconvert-venv/bin/python3';
const VENV_PIP = '/tmp/docconvert-venv/bin/pip';

function log(msg) { console.log(`[preflight] ${msg}`); }
function warn(msg) { console.warn(`[preflight WARN] ${msg}`); }
function error(msg) { console.error(`[preflight ERROR] ${msg}`); }

function runSync(cmd, args, opts = {}) {
  try {
    return execSync(cmd, { stdio: 'pipe', ...opts }).toString().trim();
  } catch (e) {
    return null;
  }
}

function which(cmd) {
  return runSync('which', [cmd]) !== null;
}

async function checkPlaywright() {
  log('检查 playwright...');
  const playwrightPath = path.join(ROOT, 'word-gen', 'node_modules', 'playwright', 'package.json');
  if (fs.existsSync(playwrightPath)) {
    log('playwright 已安装 ✅');
    return true;
  }

  log('安装 playwright...');
  try {
    execSync('npm install playwright 2>&1', {
      stdio: 'pipe',
      cwd: path.join(ROOT, 'word-gen')
    });
    log('playwright 安装成功 ✅');
    return true;
  } catch (e) {
    warn(`playwright 安装失败: ${e.message}`);
    return false;
  }
}

async function checkChromium() {
  log('检查 chromium...');
  const chromiumPath = '/tmp/chrome-linux/chrome';
  if (fs.existsSync(chromiumPath)) {
    log('chromium 已安装 ✅');
    return true;
  }

  log('安装 chromium（通过 socks5 代理下载）...');
  try {
    // 使用 socks-proxy-agent 下载 chromium
    const socksProxyAgentPath = path.join(ROOT, 'word-gen', 'node_modules', 'socks-proxy-agent', 'dist', 'index.js');
    if (!fs.existsSync(socksProxyAgentPath)) {
      execSync('npm install socks-proxy-agent 2>&1', {
        stdio: 'pipe',
        cwd: path.join(ROOT, 'word-gen')
      });
    }

    const downloadScript = `
const { SocksProxyAgent } = require('${socksProxyAgentPath}');
const https = require('https');
const http = require('http');
const fs = require('fs');

const agent = new SocksProxyAgent('socks5://10.30.5.62:1081');
const revision = '1625362';
const baseUrl = 'https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/' + revision;
const url = baseUrl + '/chrome-linux.zip';

console.log('Downloading chromium from Google Storage...');
const file = fs.createWriteStream('/tmp/chrome-linux.zip');
https.get(url, { agent }, (res) => {
  if (res.statusCode === 200) {
    res.pipe(file);
    file.on('finish', () => {
      console.log('Downloaded, extracting...');
      require('child_process').execSync('cd /tmp && unzip -q chrome-linux.zip', { stdio: 'pipe' });
      console.log('Chromium ready!');
    });
  } else {
    console.error('HTTP', res.statusCode);
    process.exit(1);
  }
}).on('error', (e) => { console.error(e.message); process.exit(1); });
`;
    execSync(`node -e "${downloadScript.replace(/"/g, '\\"').replace(/\n/g, ';')}" 2>&1`, {
      stdio: 'inherit',
      timeout: 300000
    });

    if (fs.existsSync(chromiumPath)) {
      log('chromium 安装成功 ✅');
      return true;
    }
  } catch (e) {
    warn(`chromium 安装失败: ${e.message}`);
  }
  return false;
}

async function checkPythonDocx() {
  log('检查 python-docx (venv)...');
  try {
    if (fs.existsSync(VENV_PYTHON)) {
      const out = execSync(`${VENV_PYTHON} -c "import docx; print('ok')" 2>&1`).toString();
      if (out.includes('ok')) {
        log('python-docx 已安装 ✅');
        return true;
      }
    }
  } catch (e) {}

  log('设置 python-docx venv...');
  try {
    if (!fs.existsSync('/tmp/docconvert-venv')) {
      execSync('python3 -m venv /tmp/docconvert-venv 2>&1', { stdio: 'pipe' });
    }
    const env = { ...process.env };
    delete env.http_proxy; delete env.https_proxy;
    delete env.HTTP_PROXY; delete env.HTTPS_PROXY;
    delete env.all_proxy; delete env.ALL_PROXY;
    execSync(`${VENV_PIP} install python-docx --no-proxy 2>&1`, { stdio: 'pipe', env });
    log('python-docx 安装成功 ✅');
    return true;
  } catch (e) {
    warn(`python-docx 安装失败: ${e.message}`);
    return false;
  }
}

async function main() {
  log('========== 前置依赖检查 ==========');
  log('');

  const results = {
    playwright: await checkPlaywright(),
    chromium: await checkChromium(),
    pythonDocx: await checkPythonDocx(),
  };

  log('');
  log('========== 检查结果汇总 ==========');
  const allOk = Object.values(results).every(v => v);
  if (allOk) {
    log('所有依赖检查通过 ✅');
  } else {
    const failed = Object.entries(results).filter(([,v]) => !v).map(([k]) => k);
    warn(`部分依赖缺失（将使用 fallback）：${failed.join(', ')}`);
  }

  const statusFile = '/tmp/preflight-status.json';
  fs.writeFileSync(statusFile, JSON.stringify({ ...results, allOk }, null, 2));
  log(`状态已写入 ${statusFile}`);

  process.exit(allOk ? 0 : 0);
}

main().catch(e => {
  error(`前置检查异常: ${e.message}`);
  process.exit(1);
});
