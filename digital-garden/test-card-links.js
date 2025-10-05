// Test script to check if card links work correctly
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('Navigating to Insights page...');
  await page.goto('http://localhost:4321/personal/insights/');
  await page.waitForLoadState('networkidle');

  // Get all article cards
  const cards = await page.locator('article').all();
  console.log(`Found ${cards.length} cards`);

  // Check each card's link
  for (let i = 0; i < Math.min(cards.length, 3); i++) {
    const card = cards[i];
    const title = await card.locator('h3 a').textContent();
    const href = await card.locator('h3 a').getAttribute('href');

    console.log(`\nCard ${i + 1}:`);
    console.log(`  Title: ${title.trim()}`);
    console.log(`  Link: ${href}`);

    // Click the card and check where it navigates
    console.log(`  Clicking card ${i + 1}...`);
    await card.click();
    await page.waitForLoadState('networkidle');

    const currentUrl = page.url();
    console.log(`  Current URL: ${currentUrl}`);
    console.log(`  Expected: http://localhost:4321${href}`);
    console.log(`  Match: ${currentUrl === `http://localhost:4321${href}`}`);

    // Go back to insights page
    await page.goto('http://localhost:4321/personal/insights/');
    await page.waitForLoadState('networkidle');
  }

  console.log('\n\nTest completed. Browser will stay open for manual inspection.');
  // Don't close browser automatically
  // await browser.close();
})();
