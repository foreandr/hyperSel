import nodriver as nd
import time
import random
import asyncio
from bs4 import BeautifulSoup

try:
    from . import general_utilities
    from . import proxies_utilities

except:
    import general_utilities
    import proxies_utilities

global hyperSelProxies
hyperSelProxies = None

# Async functions
async def asyc_open_browser():
    browser = await open_nodriver(headless=False, proxy=None, max_attempts=3)
    return browser

def open_browser():
    return asyncio.run(asyc_open_browser())

async def async_go_to_site(browser, url):
    page = await browser.get(url=url)
    return page

async def async_get_current_url(page):
    return await page.evaluate("window.location.href")

def get_current_url(page):
    return asyncio.run(async_get_current_url(page))

def go_to_site(browser, url):
    # REUTNRS PAGE
    return asyncio.run(async_go_to_site(browser, url))

async def async_find_best_match(page, tag):
    return await page.find(tag, best_match=True)

def find_best_match(page, tag):
    return asyncio.run(async_find_best_match(page, tag))

async def async_find_nearest_text(page, text):
    return await page.find(text=text, best_match=True)

def find_nearest_text(page, text):
    return asyncio.run(async_find_nearest_text(page, text))

async def async_find_nearest_guess(page, guess):
    return await page.find(guess, best_match=True)

def find_nearest_guess(page, guess):
    return asyncio.run(async_find_nearest_guess(page, guess))

async def async_find_all_by_css_selector(page, css_selector):
    return await page.select_all(css_selector)

def find_all_by_css_selector(page, css_selector):
    return asyncio.run(async_find_nearest_guess(page, css_selector))

async def async_send_keys_to_element(element, string):
    return await element.send_keys(str(string))

def send_keys_to_element(element, string):
    return asyncio.run(async_send_keys_to_element(element, string))

async def async_click_item(item):
    return await item.mouse_click()

def click_item(item):
    return asyncio.run(async_click_item(item))

async def async_get_site_soup(browser, site, wait=0.5):
    page = await browser.get(site)
    time.sleep(wait)
    content = await page.get_content()
    soup = BeautifulSoup(content, 'html.parser')
    return soup
    
def get_site_soup(browser, site, wait=0.5):
    return asyncio.run(async_get_site_soup(browser, site, wait))

async def open_nodriver(headless=False, proxy=None, max_attempts=3):
    global hyperSelProxies
    if proxy:
        hyperSelProxies = proxies_utilities.HyperSelProxies()
        print("SLEEPING FOR PROXY...")
        time.sleep(10)
    browser_args = ["--start-maximized"]
    browser_args.append(f"--user-agent={general_utilities.generate_random_user_agent()}")
    
    if proxy:
        start = time.time()
        
        attempts = 0
        time.sleep(5)
        while True:
            try:
                proxy_ip = random.choice(hyperSelProxies.current_proxies)
                browser_args.append(f"--proxy-server={proxy_ip}")
                print("GOT PROXY", time.time()-start)
                break
            except Exception as e:
                print(F"Failed to get proxy [ATTEMPT:{attempts}]...")
                time.sleep(10)
                attempts+=1
                
    browser = await nd.start(
        headless=headless,
        browser_args=browser_args,
        lang="en-US",
    )
    return browser

async def main_test():
    while True:
        list_of_urls = [
            'https://snse.ca/',
            #'https://realestate.snse.ca/',
            #'https://jailpdftocsv.snse.ca/',
            #'http://localhost:5000',
            #'http://realestate.localhost:5000',
            #'http://jailpdftocsv.localhost:5000',
            # 'https://www.zillow.com/homedetails/30154106_zpid',
            #'https://www.zillow.com/homedetails/2055079760_zpid',
            #'https://www.zillow.com/homedetails/2082409198_zpid',
            #'https://www.zillow.com/homedetails/30258798_zpid',
            #'https://www.zillow.com/homedetails/30398040_zpid',
            #'https://www.zillow.com/homedetails/30400280_zpid',
        ]
        browser = await open_nodriver(headless=False, proxy=False)
        page = await browser.get(url='https://snse.ca/')
        time.sleep(5)
        await custom_kill_browser(browser)

        
    await custom_kill_browser(browser)
    custom_kill_browser(browser2)
    exit()



async def custom_kill_browser(browser):
    general_utilities.kill_process_by_pid(browser._process_pid)
    try:
        hyperSelProxies.stop_threads_and_exit()
    except Exception as e:
        pass
    
if __name__ == '__main__':
    # since asyncio.run never worked (for me)
    nd.loop().run_until_complete(main_test())