const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR:', err.message));
  const base = 'https://portal-anwalts.ai';
  // Set auth cookie for live domain
  const cookie = {
    name: 'user_data',
    value: JSON.stringify({ id: 'ui-test', email: 'ui-test@example.com', name: 'UI Test', provider: 'email' }),
    domain: 'portal-anwalts.ai',
    path: '/',
    httpOnly: false,
    secure: true,
    sameSite: 'None'
  };
  await page.setCookie(cookie);

  // Dashboard test
  console.log('Navigating to /dashboard');
  await page.goto(base + '/dashboard', { waitUntil: 'networkidle2', timeout: 30000 });
  const hasBtn = await page.$('#btnStartTour') !== null;
  console.log('Has btnStartTour:', hasBtn);
  if (hasBtn) {
    await page.click('#btnStartTour').catch(()=>{});
    await page.waitForTimeout(800);
    const state = await page.evaluate(() => {
      const o = document.getElementById('tourOverlay');
      const s = document.getElementById('tourStep');
      return { overlay: !!o, step: !!s, overlayDisplay: o?.style.display || null, stepHidden: s?.classList.contains('hidden') || null };
    });
    console.log('Dashboard tour state:', JSON.stringify(state));
  }

  // Documents test
  console.log('Navigating to /documents');
  await page.goto(base + '/documents', { waitUntil: 'networkidle2', timeout: 30000 });
  const hasHelp = await page.$('#btnHelp') !== null;
  console.log('Has btnHelp:', hasHelp);
  if (hasHelp) {
    await page.click('#btnHelp').catch(()=>{});
    await page.waitForTimeout(800);
    const state = await page.evaluate(() => {
      const o = document.getElementById('tourOverlay');
      const s = document.getElementById('tourStep');
      return { overlay: !!o, step: !!s, overlayDisplay: o?.style.display || null, stepHidden: s?.classList.contains('hidden') || null };
    });
    console.log('Documents tour state:', JSON.stringify(state));
  }

  await browser.close();
})();
