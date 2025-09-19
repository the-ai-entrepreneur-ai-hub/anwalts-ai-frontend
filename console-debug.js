const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR:', err.message));
  const base = 'http://127.0.0.1:3000';
  await page.setCookie({ name: 'user_data', value: JSON.stringify({id:'ui',email:'ui@example.com'}), url: base, path: '/' });
  await page.goto(base + '/dashboard', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.evaluate(() => { console.log('btn:', !!document.getElementById('btnStartTour'));});
  await page.click('#btnStartTour');
  await page.waitForTimeout?.(500);
  await new Promise(r=>setTimeout(r,700));
  await page.evaluate(() => {
    const o = document.getElementById('tourOverlay');
    const s = document.getElementById('tourStep');
    console.log('after click display:', o?.style.display, 'hidden?', s?.classList.contains('hidden'));
  });
  await browser.close();
})();
