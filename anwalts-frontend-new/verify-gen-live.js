const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR:', err.message));

  const base = 'https://portal-anwalts.ai';
  // Set a lightweight user cookie to avoid any client checks
  await page.setCookie({ name: 'user_data', value: JSON.stringify({ id: 'ui-test', email: 'ui-test@example.com' }), domain: 'portal-anwalts.ai', path: '/', httpOnly: false, secure: true, sameSite: 'None' });

  // Open Documents
  console.log('Navigating to /documents');
  await page.goto(base + '/documents', { waitUntil: 'domcontentloaded', timeout: 45000 });

  // Try to fill inputs (best-effort based on known IDs/placeholders)
  const filled = await page.evaluate(() => {
    const docType = document.querySelector('#docType') || document.querySelector('input[placeholder*=Dokumenttyp], input[placeholder*=z.B.]');
    const req = document.querySelector('#requirements') || document.querySelector('textarea');
    if (docType) docType.value = 'NDA – Standard (DE)';
    if (req) req.value = 'Bitte generiere eine NDA mit Standardklauseln (Gerichtsstand: Berlin).';
    if (docType) docType.dispatchEvent(new Event('input')); if (req) req.dispatchEvent(new Event('input'));
    return !!(docType && req);
  });
  console.log('Filled form fields:', filled);

  // Click generate button by id or by text
  let clicked = false;
  const btnGen = await page.$('#btnGenerate');
  if (btnGen) { await btnGen.click().then(() => clicked = true).catch(()=>{}); }
  if (!clicked) {
    const buttons = await page.$$('button, a');
    for (const b of buttons) {
      const txt = (await (await b.getProperty('innerText')).jsonValue()).trim();
      if (/Dokument\s*erstellen/i.test(txt)) { await b.click().then(() => { clicked = true; }); break; }
    }
  }
  console.log('Clicked generate:', clicked);

  // Wait a bit for network/preview to update
  await page.evaluate(() => new Promise(r => setTimeout(r, 1500)));

  // Check preview content
  const result = await page.evaluate(() => {
    const preview = document.getElementById('preview');
    const previewEmpty = document.getElementById('previewEmpty');
    const overlay = document.getElementById('genOverlay');
    const textLen = preview ? (preview.innerText || '').trim().length : 0;
    return {
      hasPreview: !!preview,
      previewVisible: !!preview && !preview.classList.contains('hidden'),
      previewEmptyHidden: !!previewEmpty && previewEmpty.classList.contains('hidden'),
      overlayHidden: !!overlay && overlay.classList.contains('hidden'),
      textLen
    };
  });
  console.log('Preview state:', JSON.stringify(result));

  await browser.close();
  // Exit code based on preview content
  if (!result.previewVisible || result.textLen < 10) process.exit(2);
})();
