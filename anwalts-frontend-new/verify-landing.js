const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);
  await page.goto('https://portal-anwalts.ai/', { waitUntil: 'networkidle2' });
  const initial = page.url();
  // Click a CTA
  const ctas = await page.$$('a,button');
  for (const el of ctas) {
    const text = (await page.evaluate(e => (e.textContent||'').trim(), el)).toLowerCase();
    const href = await page.evaluate(e => e.getAttribute && e.getAttribute('href') || '', el);
    if (/registrieren|anmelden|sign\s*in|sign\s*up/.test(text) || /framer\.(com|link)/i.test(href)) {
      await el.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 1500));
  const after = page.url();
  const blocked = !/framer\.(com|link)/i.test(after);
  console.log(JSON.stringify({ initial, after, blocked }));
  await browser.close();
})();
