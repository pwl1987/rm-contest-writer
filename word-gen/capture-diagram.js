/**
 * 使用 Playwright 无头模式截图架构图 HTML
 * 用法: node capture-diagram.js <html文件路径> <输出png路径>
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

const HTML_PATH = process.argv[2];
const OUTPUT_PNG = process.argv[3];

if (!HTML_PATH || !OUTPUT_PNG) {
  console.log('用法: node capture-diagram.js <html文件路径> <输出png路径>');
  process.exit(1);
}

const CHROMIUM_PATH = '/tmp/chrome-linux/chrome';

// Start local HTTP server for the HTML file
function startHttpServer(dir, port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const pathname = new URL(req.url, `http://localhost:${port}`).pathname;
      let filePath = path.join(dir, pathname === '/' ? '/index.html' : pathname);

      if (!fs.existsSync(filePath)) {
        res.writeHead(404);
        res.end('Not Found');
        return;
      }

      const ext = path.extname(filePath);
      const contentType = ext === '.html' ? 'text/html' : ext === '.css' ? 'text/css' : 'application/octet-stream';

      res.writeHead(200, { 'Content-Type': contentType });
      fs.createReadStream(filePath).pipe(res);
    });

    server.on('error', reject);
    server.listen(port, () => resolve(port));
  });
}

async function captureDiagram() {
  const dir = path.dirname(path.resolve(HTML_PATH));
  const httpPort = 8899;

  console.log('Starting HTTP server for:', dir);
  await startHttpServer(dir, httpPort);

  console.log('Launching Chromium...');
  const browser = await chromium.launch({
    executablePath: CHROMIUM_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();

  // 设置较大视口以完整渲染架构图
  await page.setViewportSize({ width: 1280, height: 960 });

  const targetUrl = `http://localhost:${httpPort}/${path.basename(HTML_PATH)}`;
  console.log('Navigating to:', targetUrl);
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });

  // 等待图表渲染
  await page.waitForTimeout(2000);

  console.log('Taking screenshot...');
  await page.screenshot({ path: OUTPUT_PNG, type: 'png', fullPage: true });

  await browser.close();

  const size = fs.statSync(OUTPUT_PNG).size;
  console.log(`截图已保存: ${OUTPUT_PNG} (${size} bytes)`);
}

captureDiagram().catch(e => {
  console.error('截图失败:', e.message);
  process.exit(1);
});
