from playwright.async_api import async_playwright
from undetected_playwright import Tarnished, Malenia
from bs4 import BeautifulSoup
import asyncio
import general_utilities
import proxies_utilities
import colors_utilities
import random
import time


# hyperSelProxies.start_printing_proxies()
global hyperSelProxies
hyperSelProxies = None

async def create_playwright(proxy=False):
    global hyperSelProxies
    
    try:
        # Initialize proxies if using_proxies is True
        if proxy:
            hyperSelProxies = proxies_utilities.HyperSelProxies()
            delay = 7
            print(f"creating 7s {delay} to let proxies get going...")
            time.sleep(delay)
        
        # Start Playwright session
        playwright = await async_playwright().start()

        return playwright

    except Exception as e:
        colors_utilities.c_print(text=f"Error starting Playwright: {e}", color='red')
        return None

async def playwright_go_to_page(playwright, url, headless=True, max_attempts=2, use_proxy=False):

    if not use_proxy:
        print("PROXY 1")
        browser = await playwright.chromium.launch(
            headless=headless,
        )

        context_options = {
            "user_agent": general_utilities.generate_random_user_agent()
        }

        context = await browser.new_context(**context_options)
        await Malenia.apply_stealth(context)
        
        page = await context.new_page()

        try:
            await page.goto(url, timeout=10000) 
            return browser, page
        except Exception as e:
            await browser.close()
            await playwright_stop(playwright)
            # print(f"e; {e}")
            print(f"MAJOR FAIL {url}")
            return None, None
            
    else:
        print("PROXY 2")
        for attempt in range(max_attempts):

            proxy = {
                "server": random.choice(hyperSelProxies.current_proxies)
            } if hyperSelProxies.current_proxies else None
            
            print("proxy:", proxy) 
            if proxy == None and attempt <= max_attempts:
                print("NO PROXY TRYING AGAIN")
                time.sleep(5)
                attempt +=1
                continue   
            
            proxy_options = {
                 "server": proxy['server']
            } if proxy else None

            browser = await playwright.chromium.launch(
                headless=headless,
                proxy=proxy_options
            )

            context_options = {
                "user_agent": general_utilities.generate_random_user_agent()
            }

            context = await browser.new_context(**context_options)
            # await Malenia.apply_stealth(context)
            page = await context.new_page()

            try:
                # Attempt to navigate to the URL with a timeout
                await page.goto(url, timeout=10000)  # 5 seconds timeout
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

async def playwright_get_soup_from_page(page):
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

async def playwright_get_soup_from_url(playwright, url, headless=True,proxy=False, site_time_delay=0):
    browser, page = await playwright_go_to_page(
        playwright, 
        url, 
        headless=headless, 
        use_proxy=proxy
    )
    time.sleep(site_time_delay)
    soup = await playwright_get_soup_from_page(page)
    await browser.close()
    return soup
    

async def main_test():
    url = 'https://snse.ca/'
    playwright = await create_playwright()

    for i in range(100):
        browser, page = await playwright_go_to_page(playwright, url, headless=True, use_proxy=True)
        if page:
            try:
                soup = await playwright_get_soup_from_page(page)
                print(f"Iteration {i+1}: {len(str(soup))}")
            finally:
                await browser.close()
    
    await playwright_stop(playwright)

async def playwright_stop(playwright):
    try:
        hyperSelProxies.stop()
    except Exception as e:
        # NO PROXIES
        pass
    await playwright.stop()

if __name__ == '__main__':
    asyncio.run(main_test())
