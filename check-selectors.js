const puppeteer = require('puppeteer');
async function run(){
  const browser = await puppeteer.launch({ headless: 'new', args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  const base = 'http://127.0.0.1:3000';
  const user = { id: 'ui-test', email: 'ui-test@example.com', name: 'UI Test', provider: 'email' };
  await page.setCookie({ name: 'user_data', value: JSON.stringify(user), url: base, path: '/' });
  await page.goto(base + '/dashboard', { waitUntil: 'domcontentloaded', timeout: 20000 });
  const selsDash = ['#globalSearch','#btnNewDoc','#deadlines','#recentDocs','#templates','#linkAssistant'];
  const present = await page.evaluate((sels)=> sels.map(sel => [sel, !!document.querySelector(sel)]), selsDash);
  console.log('Dashboard selectors:', present);
  await page.goto(base + '/documents', { waitUntil: 'domcontentloaded', timeout: 20000 });
  const selsDoc = ['#docType','#requirements','#btnGenerate','#previewContainer'];
  const present2 = await page.evaluate((sels)=> sels.map(sel => [sel, !!document.querySelector(sel)]), selsDoc);
  console.log('Documents selectors:', present2);
  await browser.close();
}
run();
