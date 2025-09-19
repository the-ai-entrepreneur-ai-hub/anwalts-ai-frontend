const puppeteer = require('puppeteer');

async function testPortal() {
    try {
        const browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });
        
        console.log('Testing https://portal-anwalts.ai/...\n');
        
        // Listen for console errors
        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });
        
        // Navigate to page
        console.log('1. Loading page...');
        const response = await page.goto('https://portal-anwalts.ai/', { 
            waitUntil: 'networkidle0',
            timeout: 30000 
        });
        
        console.log(`   Status: ${response.status()}`);
        
        // Wait for content
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check if page content exists
        console.log('2. Checking page content...');
        const bodyText = await page.evaluate(() => document.body.innerText);
        const hasContent = bodyText && bodyText.trim().length > 0;
        
        console.log(`   - Has content: ${hasContent}`);
        console.log(`   - Content length: ${bodyText ? bodyText.length : 0} characters`);
        
        // Look for Registrieren button
        console.log('3. Looking for Registrieren button...');
        const registerButtons = await page.$$eval('*', elements => 
            elements.filter(el => 
                (el.textContent && el.textContent.toLowerCase().includes('registrieren')) ||
                (el.getAttribute && (
                    el.getAttribute('data-testid')?.includes('register') ||
                    el.className?.includes('register')
                ))
            ).map(el => ({
                tagName: el.tagName,
                text: el.textContent?.trim(),
                className: el.className,
                id: el.id,
                type: el.type
            }))
        );
        
        console.log(`   - Found ${registerButtons.length} potential register buttons`);
        registerButtons.forEach((btn, i) => {
            console.log(`   Button ${i+1}: ${btn.tagName} - "${btn.text}" (class: ${btn.className})`);
        });
        
        // Check for auth modal initially
        console.log('4. Checking for auth modal on load...');
        const modalSelectors = ['[role="dialog"]', '.modal', '[data-testid*="modal"]', '.auth-modal'];
        let modalVisible = false;
        
        for (const selector of modalSelectors) {
            try {
                const modal = await page.$(selector);
                if (modal) {
                    const isVisible = await modal.isIntersectingViewport();
                    if (isVisible) {
                        modalVisible = true;
                        console.log(`   - Modal found with selector: ${selector}`);
                        break;
                    }
                }
            } catch (e) {
                // Selector might not exist, continue
            }
        }
        
        console.log(`   - Auth modal auto-opened: ${modalVisible}`);
        
        // Try to click a register button if found
        if (registerButtons.length > 0) {
            console.log('5. Attempting to click Registrieren button...');
            try {
                const clicked = await page.evaluate(() => {
                    const buttons = Array.from(document.querySelectorAll('*')).filter(el => 
                        el.textContent && el.textContent.toLowerCase().includes('registrieren')
                    );
                    if (buttons.length > 0) {
                        buttons[0].click();
                        return true;
                    }
                    return false;
                });
                
                if (clicked) {
                    console.log('   - Button clicked successfully');
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // Check if modal appeared after click
                    let modalAppeared = false;
                    for (const selector of modalSelectors) {
                        try {
                            const modal = await page.$(selector);
                            if (modal) {
                                const isVisible = await modal.isIntersectingViewport();
                                if (isVisible) {
                                    modalAppeared = true;
                                    console.log(`   - Modal appeared after click: ${selector}`);
                                    break;
                                }
                            }
                        } catch (e) {
                            // Continue
                        }
                    }
                    console.log(`   - Modal opened after click: ${modalAppeared}`);
                } else {
                    console.log('   - No clickable button found');
                }
            } catch (error) {
                console.log(`   - Error clicking: ${error.message}`);
            }
        } else {
            console.log('5. No Registrieren button found to click');
        }
        
        // Take screenshot
        console.log('6. Taking screenshot...');
        await page.screenshot({ 
            path: '/tmp/portal-screenshot.png', 
            fullPage: true 
        });
        console.log('   - Screenshot saved');
        
        // Check console errors
        console.log('7. JavaScript console errors:');
        if (consoleErrors.length > 0) {
            consoleErrors.forEach((error, i) => {
                console.log(`   ${i+1}. ${error}`);
            });
        } else {
            console.log('   - No console errors detected');
        }
        
        // Get page title
        const title = await page.title();
        console.log(`\nPage title: "${title}"`);
        
        await browser.close();
        
        return {
            loaded: response.status() === 200,
            hasContent: hasContent,
            registrierenButtonFound: registerButtons.length > 0,
            modalAutoOpened: modalVisible,
            consoleErrors: consoleErrors
        };
        
    } catch (error) {
        console.error('Test failed:', error);
        return null;
    }
}

testPortal();