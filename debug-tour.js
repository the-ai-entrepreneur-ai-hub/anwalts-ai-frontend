const puppeteer = require('puppeteer');
async function run(){
  const browser = await puppeteer.launch({ headless: 'new', args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  const base = 'http://127.0.0.1:3000';
  const user = { id: 'ui-test', email: 'ui-test@example.com', name: 'UI Test', provider: 'email' };
  await page.setCookie({ name: 'user_data', value: JSON.stringify(user), url: base, path: '/' });
  await page.goto(base + '/dashboard', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForSelector('#btnStartTour', { timeout: 10000 });
  let state = await page.evaluate(() => {
    const o = document.getElementById('tourOverlay');
    const s = document.getElementById('tourStep');
    return { overlay: !!o, step: !!s, overlayDisplay: o?.style.display || null, stepHidden: s?.classList.contains('hidden') || null };
  });
  console.log('Initial:', state);
  await page.click('#btnStartTour');
  await new Promise(r => setTimeout(r, 800));
  state = await page.evaluate(() => {
    const o = document.getElementById('tourOverlay');
    const s = document.getElementById('tourStep');
    const content = document.getElementById('tourContent');
    return { overlay: !!o, step: !!s, overlayDisplay: o?.style.display || null, stepHidden: s?.classList.contains('hidden') || null, content: content?.innerHTML || null };
  });
  console.log('After click:', state);
  console.log('Classes:', await page.evaluate(()=>({overlay: document.getElementById('tourOverlay')?.className, step: document.getElementById('tourStep')?.className})));
  await browser.close();
}
run();
