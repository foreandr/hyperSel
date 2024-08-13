import nodriver as nd
from bs4 import BeautifulSoup
import time
import general_utilities
import colors_utilities
import proxies_utilities
import random

global hyperSelProxies
hyperSelProxies = proxies_utilities.HyperSelProxies()

async def get_site_soup(browser, site, wait=0.5):
    page = await browser.get(site)
    time.sleep(wait)
    content = await page.get_content()
    soup = BeautifulSoup(content, 'html.parser')
    return soup

async def open_nodriver(headless=False, proxy=None, max_attempts=3):
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
    list_of_urls = [
        'https://snse.ca/',
        'https://realestate.snse.ca/',
        'https://jailpdftocsv.snse.ca/',
        'https://snse.ca/',
        'https://realestate.snse.ca/',
        'https://jailpdftocsv.snse.ca/',
        # 'https://www.zillow.com/homedetails/30154106_zpid',
        #'https://www.zillow.com/homedetails/2055079760_zpid',
        #'https://www.zillow.com/homedetails/2082409198_zpid',
        #'https://www.zillow.com/homedetails/30258798_zpid',
        #'https://www.zillow.com/homedetails/30398040_zpid',
        #'https://www.zillow.com/homedetails/30400280_zpid',
    ]
    browser = await open_nodriver(headless=False, proxy=True)
    browser2 = await open_nodriver(headless=False, proxy=True)
    for url in list_of_urls:
        print("url", url)
        page = await browser.get(url=url)
        page = await browser2.get(url=url)
        # print("page", len(page))
        # time.sleep(8)
        print("done")
    
    input("STOP")
    custom_kill_browser(browser)
    custom_kill_browser(browser2)
    
def custom_kill_browser(browser):
    general_utilities.kill_process_by_pid(browser._process_pid)
    
if __name__ == '__main__':
    # since asyncio.run never worked (for me)
    nd.loop().run_until_complete(main_test())