import threading
from concurrent.futures import ThreadPoolExecutor
from itertools import islice

class HyperSelProxies:
    def __init__(self, num_workers=100):
        self.current_proxies = []
        self.proxies_to_test = []
        self.num_workers = num_workers
        
        # Event to signal threads to stop
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        # Start the proxy fetching thread
        self.proxy_thread = threading.Thread(target=self.get_new_proxies)
        self.proxy_thread.start()

        # Ensure the proxy fetching thread completes before exiting
        self.proxy_thread.join()
    
    def process_url(self, url):
        print(url)

    def process_urls(self, urls, start_index, end_index):
        for url in islice(urls, start_index, end_index):
            self.process_url(url)

    def get_new_proxies(self):
        all_urls = [
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt',
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt',
            'https://spys.one/en/free-proxy-list/',
            'https://spys.one/en/anonymous-proxy-list/',
            'https://spys.one/en/socks-proxy-list/',
            'https://spys.one/en/non-anonymous-proxy-list/',
            'https://free-proxy-list.net/',
        ]

        num_workers = self.num_workers
        total_urls = len(all_urls)
        urls_per_worker = max(total_urls // num_workers, 1)  # Avoid division by zero
        
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

if __name__ == "__main__":
    x = HyperSelProxies()
