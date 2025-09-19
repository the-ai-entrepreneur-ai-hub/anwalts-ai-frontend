const puppeteer = require('puppeteer');
async function run() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  const base = 'http://127.0.0.1:3000';
  const user = { id: 'ui-test', email: 'ui-test@example.com', name: 'UI Test', provider: 'email' };
  await page.setCookie({ name: 'user_data', value: JSON.stringify(user), url: base, path: '/' });
  await page.goto(base + '/dashboard', { waitUntil: 'domcontentloaded', timeout: 20000 });
  console.log('URL after nav:', page.url());
  const content = await page.content();
  console.log('Has btnStartTour:', content.includes('btnStartTour'));
  if (!content.includes('btnStartTour')) {
    console.log(content.substring(0, 300));
  }
  try{
    await page.waitForSelector('#btnStartTour', { timeout: 8000 });
    await page.click('#btnStartTour');
    const overlayVisible = await page.waitForFunction(() => {
      const el = document.getElementById('tourOverlay');
      const step = document.getElementById('tourStep');
      return !!el && (el.style.display === 'block' || getComputedStyle(step||el).display !== 'none');
    }, { timeout: 8000 }).then(() => true).catch(() => false);
    console.log('Dashboard tour visible:', overlayVisible);
  }catch(e){ console.log('Error on dashboard:', e.message); }

  await page.goto(base + '/documents', { waitUntil: 'domcontentloaded', timeout: 20000 });
  console.log('URL after nav docs:', page.url());
  const content2 = await page.content();
  console.log('Has btnHelp:', content2.includes('btnHelp'));
  try{
    await page.waitForSelector('#btnHelp', { timeout: 8000 });
    await page.click('#btnHelp');
    const overlayVisibleDocs = await page.waitForFunction(() => {
      const el = document.getElementById('tourOverlay');
      const step = document.getElementById('tourStep');
      return !!el && (el.style.display === 'block' || getComputedStyle(step||el).display !== 'none');
    }, { timeout: 8000 }).then(() => true).catch(() => false);
    console.log('Documents tour visible:', overlayVisibleDocs);
  }catch(e){ console.log('Error on documents:', e.message); }

  await browser.close();
}
run().catch(err => { console.error(err); process.exit(1); });
