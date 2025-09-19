const { chromium } = require('playwright');

async function testLiveSite() {
    console.log('🔍 Starting comprehensive test of https://portal-anwalts.ai/');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Capture console messages and errors
    const consoleMessages = [];
    const errors = [];
    
    page.on('console', msg => {
        consoleMessages.push({
            type: msg.type(),
            text: msg.text()
        });
        console.log(`Console ${msg.type()}: ${msg.text()}`);
    });
    
    page.on('pageerror', error => {
        errors.push(error.message);
        console.error(`Page Error: ${error.message}`);
    });
    
    page.on('requestfailed', request => {
        console.error(`Failed request: ${request.url()} - ${request.failure()?.errorText}`);
    });
    
    try {
        console.log('\n📡 1. Navigating to https://portal-anwalts.ai/');
        
        // Navigate with extended timeout
        const response = await page.goto('https://portal-anwalts.ai/', {
            waitUntil: 'domcontentloaded',
            timeout: 30000
        });
        
        console.log(`✅ HTTP Status: ${response.status()}`);
        console.log(`✅ URL after navigation: ${page.url()}`);
        
        // Wait a moment for any dynamic content
        await page.waitForTimeout(3000);
        
        console.log('\n🔍 2. Analyzing page content...');
        
        // Check if page is completely blank
        const bodyText = await page.textContent('body');
        const htmlContent = await page.content();
        
        console.log(`Body text length: ${bodyText?.length || 0}`);
        console.log(`HTML content length: ${htmlContent.length}`);
        
        // Check for basic HTML structure
        const hasHead = await page.$('head') !== null;
        const hasBody = await page.$('body') !== null;
        const hasTitle = await page.title();
        
        console.log(`Has <head>: ${hasHead}`);
        console.log(`Has <body>: ${hasBody}`);
        console.log(`Page title: "${hasTitle}"`);
        
        // Look for specific elements that should exist
        const hasReactRoot = await page.$('#root') !== null || await page.$('[id*="root"]') !== null;
        const hasApp = await page.$('[id*="app"]') !== null || await page.$('.app') !== null;
        const hasMainContent = await page.$('main') !== null;
        const hasAnyDivs = (await page.$$('div')).length;
        
        console.log(`Has React root element: ${hasReactRoot}`);
        console.log(`Has app container: ${hasApp}`);
        console.log(`Has main content: ${hasMainContent}`);
        console.log(`Number of div elements: ${hasAnyDivs}`);
        
        // Check network tab for failed resources
        console.log('\n🌐 3. Network analysis...');
        const allRequests = [];
        page.on('response', response => {
            if (response.status() >= 400) {
                console.error(`Failed resource: ${response.url()} - Status: ${response.status()}`);
            }
        });
        
        // Check if any CSS or JS files are loading
        const stylesheets = await page.$$eval('link[rel="stylesheet"]', links => 
            links.map(link => link.href)
        );
        const scripts = await page.$$eval('script[src]', scripts => 
            scripts.map(script => script.src)
        );
        
        console.log(`CSS files found: ${stylesheets.length}`);
        stylesheets.forEach(css => console.log(`  - ${css}`));
        
        console.log(`JS files found: ${scripts.length}`);
        scripts.forEach(js => console.log(`  - ${js}`));
        
        // Take a screenshot
        console.log('\n📸 4. Taking screenshot...');
        await page.screenshot({ 
            path: '/root/anwalts-frontend-new/site-screenshot.png',
            fullPage: true 
        });
        console.log('Screenshot saved to: /root/anwalts-frontend-new/site-screenshot.png');
        
        // Check viewport size and visible content
        const viewport = page.viewportSize();
        console.log(`Viewport: ${viewport.width}x${viewport.height}`);
        
        // Summary
        console.log('\n📊 SUMMARY:');
        console.log('==================');
        console.log(`HTTP Status: ${response.status()}`);
        console.log(`Page loads: ${response.status() < 400 ? '✅ YES' : '❌ NO'}`);
        console.log(`Content visible: ${(bodyText?.length || 0) > 100 ? '✅ YES' : '❌ NO'}`);
        console.log(`JavaScript errors: ${errors.length === 0 ? '✅ NONE' : `❌ ${errors.length} FOUND`}`);
        console.log(`Console messages: ${consoleMessages.length}`);
        
        if (errors.length > 0) {
            console.log('\n🚨 JavaScript Errors:');
            errors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
        }
        
        if (consoleMessages.filter(msg => msg.type === 'error').length > 0) {
            console.log('\n🚨 Console Errors:');
            consoleMessages
                .filter(msg => msg.type === 'error')
                .forEach((msg, i) => console.log(`  ${i + 1}. ${msg.text}`));
        }
        
    } catch (error) {
        console.error(`\n❌ Critical Error: ${error.message}`);
        
        // Try to take screenshot even on error
        try {
            await page.screenshot({ 
                path: '/root/anwalts-frontend-new/error-screenshot.png',
                fullPage: true 
            });
            console.log('Error screenshot saved to: /root/anwalts-frontend-new/error-screenshot.png');
        } catch (screenshotError) {
            console.error(`Failed to take screenshot: ${screenshotError.message}`);
        }
    } finally {
        await browser.close();
    }
}

// Run the test
testLiveSite().catch(console.error);