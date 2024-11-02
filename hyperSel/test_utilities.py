import threading
import time
import random
from faker import Faker
from datetime import datetime
import signal
import sys

fake = Faker()

# Corrected Import
try:
    from . import log_utilities
except Exception as e:
    import log_utilities

# Scraper functions with more frequent stop checks
def scraper1(stop_event):
    while not stop_event.is_set():
        data = [
            {
                "name": fake.name(),
                "email": fake.email(),
                "address": fake.address(),
                "company": fake.company() if random.choice([True, False]) else None
            }
            for _ in range(random.randint(10, 50))
        ]
        print("INSIDE SCRAPER1:", len(data))
        yield data
        for _ in range(4):  # 2-second delay with frequent stop checks
            if stop_event.is_set():
                print("INSIDE STOPPING")
                return
            time.sleep(0.5)

def scraper2(stop_event):
    while not stop_event.is_set():
        data = [
            {
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "company": fake.company(),
                "job": fake.job() if random.choice([True, False]) else None
            }
            for _ in range(random.randint(25, 100))
        ]
        yield data
        for _ in range(10):  # 5-second delay with frequent stop checks
            if stop_event.is_set():
                return
            time.sleep(0.5)

def scraper3(stop_event):
    while not stop_event.is_set():
        data = [
            {
                "name": fake.name(),
                "email": fake.email(),
                "address": fake.address(),
                "phone": fake.phone_number(),
                "company": fake.company(),
                "product": fake.bs() if random.choice([True, False]) else None,
                "description": fake.text() if random.choice([True, False]) else None
            }
            for _ in range(random.randint(50, 125))
        ]
        yield data
        for _ in range(20):  # 10-second delay with frequent stop checks
            if stop_event.is_set():
                return
            time.sleep(0.5)

# Function to run each scraper, process data, and log data
def run_scraper(scraper_func, name, meta_data, data_storage, stop_event):
    start_time = datetime.now()
    data_count = 0
    duplicate_count = 0
    unique_records = set()

    try:
        for data_batch in scraper_func(stop_event):
            if stop_event.is_set():
                break
            # Log the data batch
            log_utilities.log_data(data_object=data_batch)

            # Process data as before
            data_storage[name].extend(data_batch)
            data_count += len(data_batch)

            # Check for duplicates
            for record in data_batch:
                record_id = tuple(record.items())
                if record_id in unique_records:
                    duplicate_count += 1
                else:
                    unique_records.add(record_id)

            # Update metadata
            elapsed_time = (datetime.now() - start_time).total_seconds()
            rate_per_hour = data_count / (elapsed_time / 3600) if elapsed_time > 0 else 0

            # Update metadata dictionary
            meta_data[name] = {
                "running_time": elapsed_time,
                "total_data": data_count,
                "rate_per_hour": rate_per_hour,
                "duplicate_count": duplicate_count
            }
    except Exception as e:
        print(f"Error in {name}: {e}")
    finally:
        print(f"{name} has stopped.")

# Main function with immediate stop handling
def main():
    stop_event = threading.Event()  # Signal to stop threads gracefully

    meta_data = {
        "scraper1": {},
        "scraper2": {},
        "scraper3": {}
    }
    data_storage = {
        "scraper1": [],
        "scraper2": [],
        "scraper3": []
    }

    # Set up threads
    threads = [
        threading.Thread(target=run_scraper, args=(scraper1, "scraper1", meta_data, data_storage, stop_event)),
        threading.Thread(target=run_scraper, args=(scraper2, "scraper2", meta_data, data_storage, stop_event)),
        threading.Thread(target=run_scraper, args=(scraper3, "scraper3", meta_data, data_storage, stop_event))
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Signal handler to stop threads
    def signal_handler(sig, frame):
        print("\nStopping scrapers gracefully...")
        stop_event.set()  # Signal all threads to stop

    # Bind the signal handler to Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Keep the main thread active to handle signals
    try:
        while not stop_event.is_set():
            print("\nScraper Metadata Summary:")
            for scraper, stats in meta_data.items():
                print(f"{scraper}: Running Time: {stats.get('running_time', 0):.2f} seconds, "
                      f"Total Data: {stats.get('total_data', 0)}, "
                      f"Rate per Hour: {stats.get('rate_per_hour', 0):.2f}, "
                      f"Duplicate Count: {stats.get('duplicate_count', 0)}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("keyboard interupt")
        signal_handler(None, None)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    print("All scrapers stopped.")

# Run the application
if __name__ == "__main__":
    main()
