from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import random
import time

try:
    from . import general_utilities
    from . import proxies_utilities
    from . import colors_utilities
except:
    import general_utilities
    import proxies_utilities
    import colors_utilities


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

async def playwright_go_to_page(playwright, url, headless=True, max_attempts=5, use_proxy=False, stealthy=None, site_time_delay=10, full_screen=False):
    global hyperSelProxies
    if not use_proxy:
        launch_options = {
            "headless": headless
        }

        # Add the --start-maximized argument if full_screen is True

        

        browser = await playwright.chromium.launch(**launch_options)
        
        context_options = {
            "user_agent": general_utilities.generate_random_user_agent()
        }
       

        context = await browser.new_context(**context_options)
        
        page = await context.new_page()
        if full_screen:
            width = general_utilities.get_display_dimensions()['width']
            height = general_utilities.get_display_dimensions()['height']
            await page.set_viewport_size({"width": width, "height": height})

        
        try:
            try:
                await asyncio.wait_for(page.goto(url, timeout=site_time_delay*1000), timeout=site_time_delay)  # Wait for navigation with a 10-second max
            except asyncio.TimeoutError:
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

                launch_options = {
                    "headless": headless,
                    "proxy": proxy_options
                }

                # Add the --start-maximized argument if full_screen is True
                if full_screen:
                    launch_options["args"] = ['--start-maximized']

                browser = await playwright.chromium.launch(**launch_options)

                context_options = {
                    "user_agent": general_utilities.generate_random_user_agent()
                }

                context = await browser.new_context(**context_options)
                page = await context.new_page()
                await page.goto(url, timeout=site_time_delay*1000)  # 5 seconds timeout
                time.sleep(site_time_delay / 2)
                soup = await playwright_get_soup_from_page(page)
                
                if len(str(soup)) < 75:
                    await browser.close()
                    continue
                
                return browser, page

            except Exception as e:
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
        

async def playwright_get_soup_from_url(playwright, url, headless=True,proxy=False, site_time_delay=0, stealthy=False, full_screen=False):
    browser, page = await playwright_go_to_page(
        playwright, 
        url, 
        headless=headless, 
        use_proxy=proxy,
        site_time_delay=site_time_delay,
        stealthy=stealthy,
        full_screen=full_screen,
        
    )
    
    soup = await playwright_get_soup_from_page(page)
    await browser.close()
    return soup
    
async def playwright_stop(playwright):
    try:
        global hyperSelProxies
        await playwright.stop()
        hyperSelProxies.stop_threads_and_exit()
    except Exception as e:
        pass
    
if __name__ == '__main__':
    pass