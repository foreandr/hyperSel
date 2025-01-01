import nodriver as nd
import time
import random
import asyncio
from bs4 import BeautifulSoup

try:
    from . import util
    from . import tor_util
except:
    import util as util
    import tor_util as tor_util

# Async functions
async def asyc_open_browser(headless, tor):
    browser = await open_nodriver(headless, tor)
    return browser

def open_browser(headless=False, tor=False):
    return asyncio.run(asyc_open_browser(headless, tor))

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

async def open_nodriver(headless=False, tor=False):
    browser_args = ["--start-maximized"]
    browser_args.append(f"--user-agent={util.generate_random_user_agent()}")

    if tor:
        browser_args.append("--proxy-server=socks5://127.0.0.1:9050")

    browser = await nd.start(
        headless=headless,
        browser_args=browser_args,
        lang="en-US",
    )
    return browser

async def custom_kill_browser(browser):
    util.kill_process_by_pid(browser._process_pid)

def kill_browser(browser):
    asyncio.run(custom_kill_browser(browser))

def test():
    try:
        # Open the browser
        browser = open_browser(headless=False, tor=True)
        
        # Navigate to the site
        page = go_to_site(browser=browser, url="http://check.torproject.org")
        
        # Check the current URL to verify navigation
        current_url = get_current_url(page)
        print(f"Current URL: {current_url}")
        
        kill_browser(browser)
        input("--")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == '__main__':
    test()