'''
MORE SITES
# https://www.proxynova.com/proxy-server-list/country-us/

'''
import threading
import time
import requests
import re
import request_utilities
import inspect

class HyperSelProxies:
    def __init__(self, num_workers=100):
        self.current_proxies = []
        self.proxies_to_test = []
        self.num_workers = num_workers
        
        # Start the proxy fetching thread
        self.proxy_thread = threading.Thread(target=self.get_new_proxies)
        self.proxy_thread.start()

        # Start the proxy validation thread
        self.validation_thread = threading.Thread(target=self.validate_current_proxies)
        self.validation_thread.start()
        # self.stop_printing = threading.Event()
        
    def extract_proxy_addrs(self, url):
        return re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b', str(request_utilities.get_soup(url)))

    def fetch_proxies_from_url(self, url, results, index):
        proxies = self.extract_proxy_addrs(url)
        with self.lock:
            results[index] = proxies

    def get_spysone_proxies(self):
        urls = [
            'https://spys.one/en/free-proxy-list/',
            'https://spys.one/en/anonymous-proxy-list/',
            'https://spys.one/en/socks-proxy-list/',
            'https://spys.one/en/non-anonymous-proxy-list/',
            'https://free-proxy-list.net/',
        ]
        
        results = [[] for _ in urls]
        threads = []

        def fetch_url(url, index):
            try:
                proxies = self.extract_proxy_addrs(url)
                results[index] = proxies
            except Exception as e:
                print(f"Exception occurred for {url}: {e}")

        for i, url in enumerate(urls):
            thread = threading.Thread(target=fetch_url, args=(url, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # Flatten the list of lists into a single list
        proxies = [proxy for sublist in results for proxy in sublist]
        print(inspect.stack()[0][3],len(proxies))
        return proxies

    def get_speedx_proxies(self):
        urls = [
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt',
            'https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt'
        ]
        proxies = list(set([addr for url in urls for addr in self.extract_proxy_addrs(url)]))
        
        print(inspect.stack()[0][3],len(proxies))
        return proxies

    def get_freeproxy_proxies(self):
        pages = 124
        link_template = 'http://free-proxy.cz/en/proxylist/main/@PAGE_NO'
        urls = [link_template.replace('@PAGE_NO', str(page)) for page in range(1, pages + 1)]
        
        results = [[] for _ in urls]
        threads = []

        def fetch_url(url, index):
            try:
                proxies = self.extract_proxy_addrs(url)
                results[index] = proxies
            except Exception as e:
                print(f"Exception occurred for {url}: {e}")

        for i, url in enumerate(urls):
            thread = threading.Thread(target=fetch_url, args=(url, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # Flatten the list of lists into a single list
        proxies = [proxy for sublist in results for proxy in sublist]
        print(inspect.stack()[0][3],len(proxies))
        return proxies    

    def get_freeproxyworld_proxies():
        pages = 140
        link_template = 'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=@PAGE_NO'
        urls = [link_template.replace('@PAGE_NO', str(page)) for page in range(1, pages + 1)]
        results = [None] * pages
        threads = []

        def fetch_url(url, index):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    results[index] = response.json()
                else:
                    print(f"Failed to fetch {url}: Status code {response.status_code}")
            except Exception as e:
                print(f"Exception occurred for {url}: {e}")

        for i, url in enumerate(urls):
            thread = threading.Thread(target=fetch_url, args=(url, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        proxies = []
        for content in results:
            if content:
                for proxy in content.get("data", []):
                    ip = proxy.get("ip")
                    port = proxy.get("port")
                    if ip and port:
                        proxies.append(f"{ip}:{port}")

        print(inspect.stack()[0][3],len(proxies))
        return proxies
       
    def get_geonode_proxies(self):
        pages=14
        link_template = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=@PAGE_NO&sort_by=lastChecked&sort_type=desc'
        urls = [link_template.replace('@PAGE_NO', str(page)) for page in range(1, pages + 1)]

        results = [None] * pages
        threads = []

        def fetch_url(url, index):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    results[index] = response.json()
                else:
                    print(f"Failed to fetch {url}: Status code {response.status_code}")
            except Exception as e:
                print(f"Exception occurred for {url}: {e}")

        for i, url in enumerate(urls):
            thread = threading.Thread(target=fetch_url, args=(url, i))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        proxies = []
        for content in results:
            if content:
                for proxy in content.get("data", []):
                    ip = proxy.get("ip")
                    port = proxy.get("port")
                    if ip and port:
                        proxies.append(f"{ip}:{port}")

        print(inspect.stack()[0][3],len(proxies))
        return proxies
    
    def split_array(self, array, N):
        k, m = divmod(len(array), N)
        return [array[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(N)]

    def test_proxy(self, proxy):
        try:
            session = requests.Session()
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = session.get('https://httpbin.org/ip', proxies=proxies, timeout=5)
            if response.status_code == 200:
                return proxy, True, None
            else:
                return proxy, False, f"HTTP status code: {response.status_code}"
        except Exception as e:
            return proxy, False, f"RequestException: {str(e)}"
    
    def get_new_proxies(self):
        while True:
            print("PROXY LOOP")
            
            # TODO: this would preferably be threaded, instead of sequential
            self.proxies_to_test.extend(self.get_speedx_proxies())
            self.proxies_to_test.extend(self.get_geonode_proxies())
            self.proxies_to_test.extend(self.get_spysone_proxies())
            self.proxies_to_test.extend(self.get_freeproxy_proxies())
            
            print('Fetching and testing new proxies...', len(self.proxies_to_test))
            
            self.proxies_to_test = list(set(self.proxies_to_test))
            
            proxies_arr = self.split_array(array=self.proxies_to_test, N=self.num_workers)
            
            threads = []

            def worker(proxies_subarr):
                for proxy in proxies_subarr:
                    result = self.test_proxy(proxy)
                    if result[1]:  # If the proxy is valid (result is True)
                        if result[0] not in self.current_proxies:
                             self.current_proxies.append(result[0])

            for i in range(self.num_workers):
                thread = threading.Thread(target=worker, args=(proxies_arr[i],))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
                
            time.sleep(300)
            print("STARTING NEW PROXY LOOP")
              
    def get_current_proxies(self):
        return self.current_proxies

    def validate_current_proxies(self):
        print("Validating current proxies...")
        i = 0
        while True:
            while i < len(self.current_proxies):
                proxy = self.current_proxies[i]
                _, is_valid, _ = self.test_proxy(proxy)
                
                if not is_valid:
                    print(f"Removing invalid proxy: {proxy}")
                    self.current_proxies.pop(i)
                else:
                    i += 1

            print(f"Remaining valid proxies: {len(self.current_proxies)}")
            time.sleep(600)
            
        
if __name__ == "__main__":
    pass