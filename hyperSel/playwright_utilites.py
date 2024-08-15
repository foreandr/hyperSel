from playwright.async_api import async_playwright
from undetected_playwright import Tarnished, Malenia
from bs4 import BeautifulSoup
import asyncio

from . import general_utilities
from . import proxies_utilities
from . import colors_utilities

import random
import time

global hyperSelProxies
hyperSelProxies = None

async def create_playwright(proxy=False):
    global hyperSelProxies
    
    try:
        # Initialize proxies if using_proxies is True
        if proxy:
            hyperSelProxies = proxies_utilities.HyperSelProxies()
            delay = 7
            time.sleep(delay)
        
        # Start Playwright session
        playwright = await async_playwright().start()

        return playwright

    except Exception as e:
        colors_utilities.c_print(text=f"Error starting Playwright: {e}", color='red')
        return None

async def playwright_go_to_page(playwright, url, headless=True, max_attempts=5, use_proxy=False, stealthy=None, site_time_delay=10):
    if not use_proxy:
        browser = await playwright.chromium.launch(
            headless=headless,
        )

        context_options = {
            "user_agent": general_utilities.generate_random_user_agent()
        }

        context = await browser.new_context(**context_options)
        page = await context.new_page()

        try:
            try:
                await asyncio.wait_for(page.goto(url, timeout=site_time_delay*1000), timeout=site_time_delay)  # Wait for navigation with a 10-second max
            except asyncio.TimeoutError:
                # print(f"Navigation to {url} timed out, attempting to fetch content...")
                pass

            page_content = await page.content()
            return browser, page_content
        except Exception as e:
            await browser.close()
            await playwright_stop(playwright)
            print("============================")
            print("e:", e)
            print("MAJOR FAIL", url)
            return None, None
            
    else:
        for attempt in range(max_attempts):
            try:
                proxy_choice = random.choice(hyperSelProxies.current_proxies)
                proxy = {
                    "server": proxy_choice
                } if hyperSelProxies.current_proxies else None
                    
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
                page = await context.new_page()
                await page.goto(url, timeout=site_time_delay*1000)  # 5 seconds timeout
                time.sleep(site_time_delay/2)
                soup = await playwright_get_soup_from_page(page)
                
                if len(str(soup)) < 75:
                    # print("BLOCKED CONTINUE.. len(soup):", len(str(soup)))
                    await browser.close()
                    continue
                
                return browser, page

            except Exception as e:
                # print(f"Attempt {attempt + 1}: Navigation failed with proxy {proxy_choice}: {e}")
                hyperSelProxies.current_proxies.remove(proxy_choice)
                await browser.close()
                continue
            
    # FAILSAFE
    return await playwright_go_to_page(playwright, url, headless=headless, max_attempts=1, use_proxy=False)

async def playwright_get_soup_from_page(page):
    try:
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except:
        soup = BeautifulSoup(page, 'html.parser')
        return soup
        

async def playwright_get_soup_from_url(playwright, url, headless=True,proxy=False, site_time_delay=0, stealthy=False):
    browser, page = await playwright_go_to_page(
        playwright, 
        url, 
        headless=headless, 
        use_proxy=proxy,
        site_time_delay=site_time_delay,
        stealthy=stealthy,
        
    )
    
    soup = await playwright_get_soup_from_page(page)
    await browser.close()
    return soup
    
async def playwright_stop(playwright):
    await playwright.stop()
    hyperSelProxies.stop_threads_and_exit()
    
if __name__ == '__main__':
    pass