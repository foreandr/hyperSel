import nodriver as nd
from bs4 import BeautifulSoup
import time

async def get_site_soup(browser, site, wait=0.5):
    page = await browser.get(site)
    time.sleep(wait)
    content = await page.get_content()
    soup = BeautifulSoup(content, 'html.parser')
    return soup

async def open_nodriver(headless=False):
    browser = await nd.start(
        headless=headless,
        # user_data_dir="/path/to/existing/profile",  # by specifying it, it won't be automatically cleaned up when finished
        # browser_executable_path="/path/to/some/other/browser",
        # browser_args=["--some-browser-arg=true", "--some-other-option"],
        lang="en-US",  # this could set iso-language-code in navigator, not recommended to change
    )
    return browser

async def main_test():
    browser = await open_nodriver(headless=False)
    
    for i in range(4700):
        link = f'https://www.sec.gov/edgar/search/#/dateRange=30d&category=form-cat4&filter_forms=D&page={i}'
        soup = await get_site_soup(browser, link, wait=5)
        # print(soup.prettify())  # This will print the prettified HTML content
        print(i, len(str(soup)))
        
    input("STOP")

def stop_browser(browser):
    browser.stop()

if __name__ == '__main__':

    # since asyncio.run never worked (for me)
    nd.loop().run_until_complete(main_test())