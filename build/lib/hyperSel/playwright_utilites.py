from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import general_util
import proxies_util
import random

hyperSelProxies = proxies_util.HyperSelProxies()
# hyperSelProxies.start_printing_proxies()

async def create_playwright():
    return await async_playwright().start()

async def playwright_go_to_page(playwright, url, headless=True, max_attempts=2, use_proxy=False):
    if not use_proxy:
        browser = await playwright.chromium.launch(
            headless=headless,
        )

        context_options = {
            "user_agent": general_util.generate_random_user_agent()
        }

        context = await browser.new_context(**context_options)
        page = await context.new_page()

        try:
            await page.goto(url, timeout=3000) 
            return browser, page
        except Exception as e:
            await browser.close()
            await playwright_stop(playwright)
            print("MAJOR FAIL", url)
            return None, None
            
    else:
        for attempt in range(max_attempts):

            proxy = {
                "server": random.choice(hyperSelProxies.current_proxies)
            } if hyperSelProxies.current_proxies else None
                
                
            proxy_options = {
                 "server": proxy['server']
            } if proxy else None

            browser = await playwright.chromium.launch(
                headless=headless,
                proxy=proxy_options
            )

            context_options = {
                "user_agent": general_util.generate_random_user_agent()
            }

            context = await browser.new_context(**context_options)
            page = await context.new_page()

            try:
                # Attempt to navigate to the URL with a timeout
                await page.goto(url, timeout=4000)  # 5 seconds timeout
                return browser, page
            except Exception as e:
                # print(f"Attempt {attempt + 1}: Navigation failed with proxy {proxy_label}: {e}")
                await browser.close()
            
            # If not the last attempt, wait a bit before trying again
            if attempt < max_attempts - 1:
                # print("Retrying with a new proxy...")
                await asyncio.sleep(3)
    
    # FAILSAFE
    # print("FAILSAFE")
    return await playwright_go_to_page(playwright, url, headless=headless, max_attempts=1, use_proxy=False)
async def playwright_get_soup(page):
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

async def main_test():
    url = 'https://snse.ca/'
    playwright = await create_playwright()

    for i in range(100):
        browser, page = await playwright_go_to_page(playwright, url, headless=True, use_proxy=True)
        if page:
            try:
                soup = await playwright_get_soup(page)
                print(f"Iteration {i+1}:", len(str(soup)))
            finally:
                await browser.close()
    
    await playwright_stop(playwright)

async def playwright_stop(playwright):
    await playwright.stop()

if __name__ == '__main__':
    asyncio.run(main_test())
