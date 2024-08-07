import nodriver as nd
from bs4 import BeautifulSoup
import time
import general_util

async def get_site_soup(browser, site, wait=0.5):
    page = await browser.get(site)
    time.sleep(wait)
    content = await page.get_content()
    soup = BeautifulSoup(content, 'html.parser')
    return soup

async def open_nodriver(headless=False, user_agent=None):
    browser_args = ["--start-maximized"]
    if user_agent:
        browser_args.append(f"--user-agent={user_agent}")

    browser = await nd.start(
        headless=headless,
        browser_args=browser_args,
        lang="en-US",
    )
    return browser

async def main_test():
    browser = await open_nodriver(headless=False)
    
    
    page = await browser.get(url='https://snse.ca/')
    input("1111")
    print("browser:", browser)
    custom_kill_browser(browser)

def custom_kill_browser(browser):
    general_util.kill_process_by_pid(browser._process_pid)
    
if __name__ == '__main__':

    # since asyncio.run never worked (for me)
    nd.loop().run_until_complete(main_test())