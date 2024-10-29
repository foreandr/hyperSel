import nodriver as nd
from bs4 import BeautifulSoup
import time
import random
import asyncio

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

def go_to_site(browser, url):
    return asyncio.run(async_go_to_site(browser, url))

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