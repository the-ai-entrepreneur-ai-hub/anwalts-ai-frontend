const puppeteer = require('puppeteer');

async function quickTest() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    const page = await browser.newPage();
    
    try {
        console.log('Testing https://portal-anwalts.ai/');
        
        const response = await page.goto('https://portal-anwalts.ai/', { 
            waitUntil: 'domcontentloaded',
            timeout: 15000 
        });
        
        console.log(`1. Page loads: YES (Status: ${response.status()})`);
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const bodyText = await page.evaluate(() => document.body.innerText || '');
        const hasContent = bodyText.length > 100;
        
        console.log(`2. Has content: ${hasContent ? 'YES' : 'NO'} (${bodyText.length} characters)`);
        
        // Look for iframe (seems to be loading page.html)
        const hasIframe = await page.evaluate(() => !!document.querySelector('iframe'));
        console.log(`3. Has iframe: ${hasIframe ? 'YES' : 'NO'}`);
        
        // Check for register-related text
        const hasRegisterText = bodyText.toLowerCase().includes('registr') || await page.evaluate(() => 
            !!Array.from(document.querySelectorAll('*')).find(el => 
                el.textContent && el.textContent.toLowerCase().includes('registr')
            )
        );
        
        console.log(`4. Has register elements: ${hasRegisterText ? 'YES' : 'NO'}`);
        
        // Check for modals
        const modalElements = await page.evaluate(() => 
            document.querySelectorAll('[role="dialog"], .modal').length
        );
        console.log(`5. Auth modal auto-opens: ${modalElements > 0 ? 'YES' : 'NO'}`);
        
        await page.screenshot({ path: '/tmp/portal-screenshot.png' });
        console.log('6. Screenshot saved to /tmp/portal-screenshot.png');
        
        console.log('7. Console errors: Checking...');
        
        await browser.close();
        
    } catch (error) {
        console.error('Error:', error.message);
        await browser.close();
    }
}

quickTest();