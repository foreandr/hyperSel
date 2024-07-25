import time
from bs4 import BeautifulSoup
import gc
import asyncio
import nodriver as uc
# import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

def enter_keys(driver, xpath, content_to_enter, time=10):
    input_field =  WebDriverWait(driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
    input_field.clear()
    input_field.send_keys(content_to_enter)

def enter_keys_by_id(driver, element_id, keys_to_enter):
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, element_id)))
    element.clear()  # Optional: Clear any existing content in the input field
    element.send_keys(keys_to_enter)

def enter_keys_by_class(driver, element_class, keys_to_enter):
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, element_class)))
    element.clear()  # Optional: Clear any existing content in the input field
    element.send_keys(keys_to_enter)

def click_button(driver, xpath, time=5):
    element = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
    element.click()

def click_button_by_tag(driver, tag_name):
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, tag_name)))
    button.click()

def get_element_by_class(driver, class_name):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    return element

def get_element_by_css_selector(driver, css_selector, condition):
    # Condition can be either "visible" or "clickable"
    if condition == "visible":
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    elif condition == "clickable":
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
    else:
        raise ValueError("Invalid condition. Use 'visible' or 'clickable'.")
    
    return element

def click_button_by_class(driver, class_name):
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    button.click()

def begnign_click(driver):
    print("begnign_click")
    # SOMETIMES FACEBOOK NEEDS ITS SCREEN CLICKED TO BE USED
    action_chains = ActionChains(driver)
    action_chains.move_by_offset(1, 1).context_click().perform()

def click_screen(driver):
    for i in range(0,3):
        try:
            actions = ActionChains(driver)
            actions.move_by_offset(100, 100)  # Move to the bottom
            actions.context_click()  # Perform a right-click
            actions.perform()
            time.sleep(1)  
        except:
            continue
    #colors.print_error(f"[RIGHT-CLICKED SCREEN][viewport_height:{viewport_height}][viewport_width:{viewport_width}]")
    
def click_button_by_id(driver, button_id):
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id)))
    button.click()

def get_driver_soup(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    return soup

def scroll_n_times_or_to_bottom(driver, num_scrolls, time_between_scrolls=0, log=False):
    scroll_count = 0

    while scroll_count < num_scrolls:
        height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(time_between_scrolls)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == height:
            break

        scroll_count += 1
    if log:
        print("TIMES SCROLLED", scroll_count)

def scroll_to_bottom_of_element(driver, element, time_between_scrolls=0):
    scroll_iters = 0
    while True:
        if scroll_iters >= 10:
            break
        scroll_iters +=1
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)
        time.sleep(time_between_scrolls)
        
def scroll_element_n_times(driver, element, time_between_scrolls, num_scrolls):
    scroll_iters = 0
    while True:
        if scroll_iters >=  num_scrolls:
            break
        scroll_iters +=1
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)
        time.sleep(time_between_scrolls)  # Add a delay if needed

def default_scroll_to_buttom(driver, time_between_scrolls=0):
    height = driver.execute_script("return document.body.scrollHeight")
    while True:
        time.sleep(time_between_scrolls)  # Add a 1-second delay
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == height:
            break
        height = new_height

def scroll_until_element_in_view(driver, xpath, time=60):
    element = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def scroll_up_n_pixels(driver, pixels):
    # Scroll up by specified number of pixels using JavaScript
    driver.execute_script(f"window.scrollBy(0, -{pixels});")

def close_driver(driver):
    try:
        driver.quit()
        driver = None
        gc.collect()
        return None
    except:
        print("ERROR CLOSING DRIVER")

def select_element_by_id(driver, id, time=20):
    select_element = WebDriverWait(driver, time).until(EC.element_to_be_clickable((By.ID, id)))
    return select_element

def select_element_by_xpath(driver, xpath, timeout=10):
    # Wait for the element to be present and visible
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    return element

def select_multiple_elements_by_xpath(driver, xpath, timeout=10):
    try:
        # Wait for the elements to be present and visible
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        return elements
    except Exception as e:
        print(f"Elements not found or couldn't be interacted with: {e}")
        return []
    
def select_multiple_elements_by_css_selector(driver, css_selector, timeout=10):
    try:
        # Wait for the elements to be present and visible
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        )
        return elements
    except Exception as e:
        print(f"Elements not found or couldn't be interacted with: {e}")
        return []

def create_select_object_from_element(element):
    select = Select(element)
    return select

def go_to_site(driver, site, tries=10):
    for i in range(tries):
        try:
            driver.get(site)
            return True
        except Exception as e:
            print(e)
            continue
        
    print("FAILED TO GO TO SITE AFTER N TRIES")
    return False
            
def open_site_selenium(site, show_browser=False):
    options = Options()
    if not show_browser:
        options.add_argument("--headless") # Run in headless mode

    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    go_to_site(driver, site)
    return driver



'''
def open_site_selenium_undetected(site, show_browser=False):
    options = Options()
    if not show_browser:
        options.add_argument("--headless") # Run in headless mode
    
    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(site)
    return driver
'''

def maximize_the_window(driver):
    try:
        driver.maximize_window()
    except Exception as e:
        print(e)
        
def minimize_window(driver):
    try:
        driver.minimize_window()
    except Exception as e:
        print(e)

def left_click_center_of_screen(driver):
    # Get the size of the browser window to calculate the center point
    window_width = driver.execute_script("return window.innerWidth;")
    window_height = driver.execute_script("return window.innerHeight;")

    # Calculate the middle of the screen
    x = window_width / 2
    y = window_height / 2

    # Create an ActionChains instance and perform a left-click on the middle of the screen
    action_chains = ActionChains(driver)
    action_chains.move_by_offset(x, y)
    action_chains.click()
    action_chains.perform()

def take_screenshot(driver, file_path="./pics"):
    driver.save_screenshot(file_path)

if __name__ == '__main__':
    pass