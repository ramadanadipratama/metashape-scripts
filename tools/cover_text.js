// Add title, subtitle and author text to a cover image (3:4) with real fonts.
// Usage: node tools/cover_text.js <art.png> <book.json> <fonts-dir> <out.png>
// fonts-dir must hold archivo.woff2 (variable) and newsreader-500-italic.woff2.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const [art, bookJson, fontsDir, out] = process.argv.slice(2);
if (!out) { console.error('Usage: node tools/cover_text.js <art.png> <book.json> <fonts-dir> <out.png>'); process.exit(1); }

const b64 = p => fs.readFileSync(p).toString('base64');
const meta = JSON.parse(fs.readFileSync(bookJson, 'utf8'));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
// Canvas follows the art's own aspect ratio (PNG/JPEG size read from the file header).
const imgSize = file => {
  const d = fs.readFileSync(file);
  if (d.readUInt32BE(0) === 0x89504e47) return [d.readUInt32BE(16), d.readUInt32BE(20)];
  for (let i = 2; i < d.length;) {            // JPEG: walk segments to the SOF marker
    const m = d[i + 1], len = d.readUInt16BE(i + 2);
    if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return [d.readUInt16BE(i + 7), d.readUInt16BE(i + 5)];
    i += 2 + len;
  }
  return [3, 4];
};
const [iw, ih] = imgSize(art);
const W = 1500, H = Math.round(W * ih / iw);

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Archivo;src:url(data:font/woff2;base64,${b64(path.join(fontsDir, 'archivo.woff2'))}) format('woff2');font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:Newsreader;src:url(data:font/woff2;base64,${b64(path.join(fontsDir, 'newsreader-500-italic.woff2'))}) format('woff2');font-style:italic;font-weight:500}
html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:#0d1f26}
.art{position:absolute;inset:0;background:url(data:image/png;base64,${b64(art)}) center/cover no-repeat}
.top{position:absolute;inset:0 0 auto 0;height:46%;background:linear-gradient(to bottom,rgba(8,24,28,.88) 0%,rgba(8,24,28,.55) 60%,rgba(8,24,28,0) 100%)}
.bot{position:absolute;inset:auto 0 0 0;height:30%;background:linear-gradient(to right,rgba(8,24,28,.85) 0%,rgba(8,24,28,.6) 35%,rgba(8,24,28,0) 58%)}
.head{position:absolute;left:110px;right:110px;top:120px;color:#f3eee2}
.eyebrow{font:600 30px/1 Archivo,sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#8ff3ff}
h1{margin:34px 0 0;font-family:Archivo,sans-serif;font-weight:850;font-stretch:112%;font-size:150px;line-height:.92;letter-spacing:-.01em;text-shadow:0 6px 30px rgba(0,0,0,.45)}
h1 span{display:block;color:#e8c46a}
.sub{margin-top:34px;font:italic 500 60px/1.15 Newsreader,Georgia,serif;color:#f3eee2}
.author{position:absolute;left:110px;bottom:120px;max-width:620px;color:#f3eee2}
.label{font:600 26px/1 Archivo,sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#8ff3ff}
.name{margin-top:18px;font-family:Archivo,sans-serif;font-weight:760;font-size:74px;line-height:1.02;text-shadow:0 4px 20px rgba(0,0,0,.5)}
</style></head><body>
<div class="art"></div><div class="top"></div><div class="bot"></div>
<div class="head">
  <div class="eyebrow">Tutorial karbon hutan · drone</div>
  <h1>${esc(meta.title).replace(/,\s*/, ',<span>')}</span></h1>
  <div class="sub">${esc(meta.subtitle || '')}</div>
</div>
<div class="author"><div class="label">Penulis</div><div class="name">${esc(meta.author || '')}</div></div>
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.setContent(html);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out });
  await browser.close();
  console.log(out);
})();
