const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);
  await page.goto('https://portal-anwalts.ai/anwalts-ai-app.html', { waitUntil: 'networkidle' });
  // Trigger modal
  await page.evaluate(() => { if (typeof window.openAuthModal==='function') window.openAuthModal(); });
  // Type email + password
  await page.fill('#authEmail', 'test@example.com');
  await page.fill('#authPassword', 'Password123!');
  // Click Anmelden; ensure we don't navigate away to framer
  const before = page.url();
  const btn = page.locator('#authSubmit, button:has-text("Anmelden")').first();
  if (await btn.count()) { await btn.click(); }
  await page.waitForTimeout(1200);
  const after = page.url();
  const stayed = !/framer\.(com|link)/i.test(after);
  console.log(JSON.stringify({ before, after, stayed }));
  await browser.close();
})();
