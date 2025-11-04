const puppeteer = require('puppeteer');
async function run(){
  const browser = await puppeteer.launch({ headless: 'new', args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  page.on('console', msg => console.log('BROWSER:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR:', err.message));
  const base = 'http://127.0.0.1:3000';
  const user = { id: 'ui-test', email: 'ui-test@example.com', name: 'UI Test', provider: 'email' };
  await page.setCookie({ name: 'user_data', value: JSON.stringify(user), url: base, path: '/' });
  await page.goto(base + '/dashboard', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.evaluate(() => 'ready');
  await page.click('#btnStartTour').catch(()=>{});
  await new Promise(r=>setTimeout(r,800));
}
run();
