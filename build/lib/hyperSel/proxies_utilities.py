import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
import random
import re
import requests
import time
try:
    from . import request_utilities
except:
    import request_utilities

class HyperSelProxies:
    def __init__(self, num_workers=5012, num_sub_workers=2048):
        self.current_proxies = []
        self.num_workers = num_workers
        self.num_sub_workers = num_sub_workers
        
        # Event to signal threads to stop
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        # Start the proxy fetching thread
        self.proxy_fetching_thread = threading.Thread(target=self.get_new_proxies)
        self.proxy_fetching_thread.start()

        self.proxy_validation_thread = threading.Thread(target=self.validate_current_proxies)
        self.proxy_validation_thread.start()
    
    def stop_threads_and_exit(self):
        # Signal the threads to stop
        self.stop_event.set()

        # Wait for the threads to finish
        self.proxy_fetching_thread.join()
        self.proxy_validation_thread.join()

    def process_single_proxy(self, proxy):
        """Process each proxy to determine if it should be added to current_proxies."""
        if self.test_proxy(proxy):  # Check if the proxy is even
            with self.lock:
                self.current_proxies.append(proxy)

    def process_proxies(self, proxies, start_index, end_index):
        """Process a slice of proxies in its own thread."""
        for proxy in islice(proxies, start_index, end_index):
            self.process_single_proxy(proxy)

    def get_new_proxies(self):
        """Fetch new proxies and process them."""
        all_urls = [
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt',
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt',
            'https://spys.one/en/free-proxy-list/',
            'https://spys.one/en/anonymous-proxy-list/',
            'https://spys.one/en/socks-proxy-list/',
            'https://spys.one/en/non-anonymous-proxy-list/',
            'https://free-proxy-list.net/',
        ]
        #all_urls.extend(['https://iproyal.com/free-proxy-list/?page=@PAGE_NO'.replace('@PAGE_NO', str(page)) for page in range(1, 650 + 1)])
        #all_urls.extend(['http://free-proxy.cz/en/proxylist/main/@PAGE_NO'.replace('@PAGE_NO', str(page)) for page in range(1, 124 + 1)])
        #all_urls.extend(['https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=@PAGE_NO'.replace('@PAGE_NO', str(page)) for page in range(1, 140 + 1)])
        #all_urls.extend(['https://proxylist.geonode.com/api/proxy-list?limit=500&page=@PAGE_NO&sort_by=lastChecked&sort_type=desc'.replace('@PAGE_NO', str(page)) for page in range(1, 14 + 1)])

        
        # print("all_urls", len(all_urls))

        num_workers = self.num_workers
        total_urls = len(all_urls)
        urls_per_worker = max(total_urls // num_workers, 1)  # Avoid division by zero
        # print('urls_per_worker:', urls_per_worker)
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                start_index = i * urls_per_worker
                end_index = start_index + urls_per_worker

                if start_index >= total_urls:
                    break  # No more URLs to process

                future = executor.submit(self.process_urls, all_urls, start_index, min(end_index, total_urls))
                futures.append(future)

            # Wait for all futures to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error: {e}")

    def process_urls(self, urls, start_index, end_index):
        """Process a list of URLs, fetching proxies and processing them."""
        for url in islice(urls, start_index, end_index):
            # print(start_index, end_index, "url:", url)
            # Simulate fetching proxies from each URL
            proxies = self.extract_proxy_addrs(url, extra_headers=None)
            
            # Divide the proxies among sub-workers
            num_sub_workers = self.num_sub_workers
            total_numbers = len(proxies)
            numbers_per_worker = max(total_numbers // num_sub_workers, 1)  # Avoid division by zero
            
            with ThreadPoolExecutor(max_workers=num_sub_workers) as sub_executor:
                sub_futures = []
                for j in range(num_sub_workers):
                    sub_start_index = j * numbers_per_worker
                    sub_end_index = sub_start_index + numbers_per_worker

                    if sub_start_index >= total_numbers:
                        break  # No more proxies to process

                    sub_future = sub_executor.submit(self.process_proxies, proxies, sub_start_index, min(sub_end_index, total_numbers))
                    sub_futures.append(sub_future)

                # Wait for all sub-futures to complete
                for sub_future in sub_futures:
                    try:
                        sub_future.result()
                    except Exception as e:
                        print(f"Sub-error: {e}")

    def extract_proxy_addrs(self, url, extra_headers=None):
        # Define the regex pattern to match IP addresses with optional port numbers
        proxy_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b'
        
        # If there are no current proxies, extract addresses with the regex pattern
        if len(self.current_proxies) == 0:
            return re.findall(proxy_pattern, str(request_utilities.get_soup(
                url=url,
                extra_headers=extra_headers,
            )))
        else:
            try:
                # Extract addresses using the regex pattern with a randomly chosen proxy
                return re.findall(proxy_pattern, str(request_utilities.get_soup(
                    url=url,
                    extra_headers=extra_headers,
                    proxy=random.choice(self.current_proxies)
                )))
            except Exception as e:
                # Fallback to extraction without proxy if an exception occurs
                return re.findall(proxy_pattern, str(request_utilities.get_soup(
                    url=url,
                    extra_headers=extra_headers,
                )))
            
    def test_proxy(self, proxy):
        try:
            session = requests.Session()
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = session.get('https://httpbin.org/ip', proxies=proxies, timeout=4)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False
        
    def validate_current_proxies(self):
        while not self.stop_event.is_set():
            i = 0
            while i < len(self.current_proxies):
                if self.stop_event.is_set():
                    return
                proxy = self.current_proxies[i]
                is_valid = self.test_proxy(proxy)
                
                if not is_valid:
                    with self.lock:
                        self.current_proxies.remove(proxy)
                else:
                    i += 1
            if self.stop_event.is_set():
                break
            time.sleep(15)
            
if __name__ == "__main__":
    pass
    
