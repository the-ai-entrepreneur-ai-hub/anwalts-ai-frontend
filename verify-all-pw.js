const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);
  // Test index
  await page.goto('https://portal-anwalts.ai/', { waitUntil: 'networkidle' });
  const before1 = page.url();
  // Click many candidates
  const sels = ['text=Registrieren','text=Anmelden','role=button[name=/Registrieren|Anmelden/i]','a[href*="framer"],button:has-text("Registrieren")'];
  for (const s of sels) { try { const loc = page.locator(s).first(); if (await loc.count()) { await loc.click(); break; } } catch {} }
  await page.waitForTimeout(1200);
  const after1 = page.url();
  const ok1 = !/framer\.(com|link)/i.test(after1);
  // Test anwalts-ai-app.html
  await page.goto('https://portal-anwalts.ai/anwalts-ai-app.html', { waitUntil: 'networkidle' });
  const before2 = page.url();
  const sels2 = ['text=Registrieren','text=Anmelden','a[href*="framer"],button:has-text("Registrieren")'];
  for (const s of sels2) { try { const loc = page.locator(s).first(); if (await loc.count()) { await loc.click(); break; } } catch {} }
  await page.waitForTimeout(1200);
  const after2 = page.url();
  const ok2 = !/framer\.(com|link)/i.test(after2);
  console.log(JSON.stringify({ index: {before: before1, after: after1, blocked: ok1}, app: {before: before2, after: after2, blocked: ok2} }));
  await browser.close();
})();
