const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);
  await page.goto('https://portal-anwalts.ai/', { waitUntil: 'networkidle' });
  // Try a set of registration/login CTAs
  const candidates = [
    'text=/Registrieren|Anmelden/i',
    'a[href*="framer"]',
    'button:has-text("Registrieren")'
  ];
  for (const sel of candidates) {
    const loc = page.locator(sel).first();
    if (await loc.count()) { await loc.click(); break; }
  }
  await page.waitForTimeout(1200);
  const after = page.url();
  console.log(JSON.stringify({ after }));
  await browser.close();
})();
