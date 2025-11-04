const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://portal-anwalts.ai/', { waitUntil: 'networkidle' });
  const initial = page.url();
  // Try header Login/Registrieren button
  const candidates = [
    'text=Registrieren',
    'text=Anmelden',
    'role=button[name=/Registrieren|Anmelden/i]'
  ];
  let clicked = false;
  for (const sel of candidates) {
    try { await page.locator(sel).first().click({ trial: false }); clicked = true; break; } catch {}
  }
  if (!clicked) {
    // click any framer anchor if exists
    const framer = page.locator('a[href*="framer"]');
    if (await framer.count()) { await framer.first().click(); clicked = true; }
  }
  await page.waitForTimeout(1200);
  const after = page.url();
  const blocked = !/framer\.(com|link)/i.test(after);
  console.log(JSON.stringify({ initial, after, blocked }));
  await browser.close();
})();
