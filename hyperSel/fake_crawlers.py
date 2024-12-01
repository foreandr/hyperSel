try:
    from . import log_utilities
except:
    import log_utilities
    
import random
import time
from faker import Faker
fake = Faker()

# Define individual scrapers here
def scraper1(stop_event):
    while not stop_event.is_set():
        data = [{"name": fake.name(), "email": fake.email(), "address": fake.address(), "company": fake.company()} for _ in range(random.randint(10, 50))]
        log_utilities.log_data(data_object=data)
        for _ in range(4):  
            if stop_event.is_set():
                return
            time.sleep(0.5)

def scraper2(stop_event):
    while not stop_event.is_set():
        data = [{"name": fake.name(), "email": fake.email(), "phone": fake.phone_number(), "company": fake.company()} for _ in range(random.randint(25, 100))]
        log_utilities.log_data(data_object=data)
        for _ in range(10): 
            if stop_event.is_set():
                return
            time.sleep(0.5)

def scraper3(stop_event):
    while not stop_event.is_set():
        data = [{"name": fake.name(), "email": fake.email(), "phone": fake.phone_number(), "company": fake.company()} for _ in range(random.randint(50, 125))]
        log_utilities.log_data(data_object=data)
        for _ in range(20):  
            if stop_event.is_set():
                return
            time.sleep(0.5)