const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:4322/personal/insights/claude-45-evolution-autonomy-dev-support/');
  await page.waitForLoadState('networkidle');

  // Take full page screenshot
  await page.screenshot({ path: 'debug-full.png', fullPage: true });

  // Take screenshot of just the content area
  const content = await page.locator('.prose').first();
  await content.screenshot({ path: 'debug-content.png' });

  // Get computed styles of h2
  const h2Styles = await page.locator('h2').first().evaluate(el => {
    const computed = window.getComputedStyle(el);
    return {
      fontSize: computed.fontSize,
      fontWeight: computed.fontWeight,
      borderBottom: computed.borderBottom,
      marginTop: computed.marginTop,
      marginBottom: computed.marginBottom
    };
  });

  console.log('H2 Computed Styles:', JSON.stringify(h2Styles, null, 2));

  await browser.close();
  console.log('Screenshots saved: debug-full.png, debug-content.png');
})();
