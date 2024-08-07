from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import general_util
import proxies_util
import random
import time

hyperSelProxies = proxies_util.HyperSelProxies()
# hyperSelProxies.start_printing_proxies()

async def create_playwright():
    return await async_playwright().start()

async def playwright_go_to_page(playwright, url, headless=True, proxy=None):
    browser = await playwright.chromium.launch(
        headless=headless,
        proxy=proxy
    )
    
    context_options = {
        "user_agent": general_util.generate_random_user_agent()
    }

    context = await browser.new_context(**context_options)
    page = await context.new_page()

    try:
        # Attempt to navigate to the URL with a timeout
        await page.goto(url, timeout=3000)  # 5 seconds timeout
    except Exception as e:
        print(f"Navigation failed: {e}")
        await browser.close()
        return None, None
    
    return browser, page

async def playwright_get_soup(page):
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

async def main():
    url = 'https://snse.ca/'
    playwright = await create_playwright()
    
    for i in range(100):
        proxy_attempts = 0
        success = False
        
        while proxy_attempts < 3 and not success:
            if proxy_attempts > 0:
                print("Trying a new proxy...")
            if hyperSelProxies.current_proxies:
                proxy = {
                    "server": random.choice(hyperSelProxies.current_proxies)
                }
            else:
                proxy = None  # No proxies available, will make a direct request

            browser, page = await playwright_go_to_page(playwright, url, headless=True, proxy=proxy)
            
            if page:
                try:
                    soup = await playwright_get_soup(page)
                    # Process your soup object here
                    print(f"Iteration {i+1}:")
                    # Example: print the prettified HTML
                    # print(soup.prettify())
                    success = True
                finally:
                    await browser.close()
            else:
                proxy_attempts += 1
        
        if not success:
            # Make a normal request if all proxies fail
            print("All proxies failed, making a normal request...")
            browser, page = await playwright_go_to_page(playwright, url, headless=True, proxy=None)
            if page:
                try:
                    soup = await playwright_get_soup(page)
                    # Process your soup object here
                    print(f"Iteration {i+1} (Normal Request):")
                    # Example: print the prettified HTML
                    # print(soup.prettify())
                finally:
                    await browser.close()
    
    await playwright.stop()

if __name__ == '__main__':
    asyncio.run(main())
