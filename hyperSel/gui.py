import customtkinter as ctk
import json
import webbrowser
import re
from PIL import Image
from PIL import UnidentifiedImageError
import requests
from io import BytesIO
import datetime
from threading import Event, Thread
from collections import Counter
import random
import config

# Initialize the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GUI(ctk.CTk):
    
    # --------------- Initialization and Main Window Setup ---------------
    
    def __init__(self, path="./logs/crawl_data.json"):
        super().__init__()
        self.title("Hypersel")
        self.after(100, lambda: self.state("zoomed"))

        # Track the current page index
        self.current_page = 0
        # print("\nApplication initialized.")

        try:
            with open(path, 'r') as file:
                self.data_entries = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Warning: Unable to load data from {path}. Initializing with an empty data list.")
            self.data_entries = []  # Initialize as an empty list if loading fails

        # Set up the main tab view containing "Data" and "Crawlers" tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        # print("\nMain tab view created.")

        # --------------- Data Tab and Content ---------------
        data_tab = self.tabview.add("Data")
        # print("\nData tab initialized.")
        
        # Grid configuration for Data tab layout
        data_tab.grid_columnconfigure(0, weight=1)  # Give all remaining space to data area
        data_tab.grid_columnconfigure(1, weight=0)  # Remove expansion for the filter column
        data_tab.grid_rowconfigure(1, weight=1)

        # Header for the Data tab
        label_button_frame = ctk.CTkFrame(data_tab)
        label_button_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="we")

        # Add a search entry field on the left
        search_entry = ctk.CTkEntry(label_button_frame, placeholder_text="Search...", width=200)
        search_entry.pack(side="left", padx=10)

        # Add the search button next to the search entry
        search_button = ctk.CTkButton(label_button_frame, text="Search", width=70, command=lambda: self.search_data(search_entry.get()))
        search_button.pack(side="left", padx=5)

        # Place the "Download" button on the far right side
        download_button = ctk.CTkButton(label_button_frame, text="Download", width=120)
        download_button.pack(side="right", padx=10)

        # Scrollable frame to display the data entries
        self.data_frame = ctk.CTkScrollableFrame(data_tab)
        self.data_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        # print("\nData scrollable frame created.")

        # Placeholder for filter sidebar
        filter_frame = ctk.CTkFrame(data_tab, width=200)  # Set fixed width for the filter frame
        filter_frame.grid(row=0, column=1, rowspan=2, padx=(10, 0), pady=10, sticky="ne")  # Align to the top-right

        # Add the "Filter/Sort" label at the top of filter_frame
        filter_label = ctk.CTkLabel(filter_frame, text="Filter / Sort", font=("Arial", 16))
        filter_label.pack(anchor="w", padx=10, pady=(5, 10))  # Adds a bit of space below the label

        print("\nFilters section header created.")

        # Store references to buttons and states
        self.filter_buttons = {}
        self.active_filters = {}

        # Initialize filter buttons based on JSON keys
        if self.data_entries:
            json_keys = self.get_all_keys(lst = self.data_entries)
            for key in json_keys:
                self.active_filters[key] = False

                # Create a frame for the left "Hello World", filter button, and right "Hello World" button
                filter_button_frame = ctk.CTkFrame(filter_frame)
                filter_button_frame.pack(anchor="w", padx=10, pady=2)  # No fill="x" to avoid expansion

                # Create the "Hello World" button on the left side
                hello_button_left = ctk.CTkButton(
                    filter_button_frame,
                    text="Asc",
                    width=40,
                    command=lambda k=key: self.sort_data(ordering='Asc', key=k)  # Pass self.sort_data with ordering and key
                )
                hello_button_left.pack(side="left", padx=5)

                # Create a toggle button for each key (Filter button)
                toggle_button = ctk.CTkButton(
                    filter_button_frame,
                    text=f"Must Have {key.capitalize()}",  # Filter
                    width=150,
                    fg_color="gray",
                    command=lambda k=key: self.toggle_filter(k)
                )
                toggle_button.pack(side="left", padx=5)

                # Create the "Hello World" button on the right side
                hello_button_right = ctk.CTkButton(
                    filter_button_frame,
                    text="Desc",
                    width=40,
                    command=lambda k=key: self.sort_data(ordering='Desc', key=k)  # Pass self.sort_data with ordering and key
                )
                hello_button_right.pack(side="left", padx=5)

                # Store the filter button reference
                self.filter_buttons[key] = toggle_button

        # --------------- Pagination Controls ---------------

        self.pagination_frame = ctk.CTkFrame(data_tab)
        self.pagination_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")  # Align the entire frame to the left

        # Update Pagination button labels
        self.btn_beginning = ctk.CTkButton(self.pagination_frame, text="First", width=50, command=self.go_to_beginning)
        self.btn_beginning.pack(side="left", padx=5)  # Align to left

        self.btn_back = ctk.CTkButton(self.pagination_frame, text="Prev", width=50, command=self.go_back)
        self.btn_back.pack(side="left", padx=5)  # Align to left

        self.page_label = ctk.CTkLabel(self.pagination_frame, text=self.get_page_label_text(len(self.data_entries)))
        self.page_label.pack(side="left", padx=5)  # Align to left

        self.btn_forward = ctk.CTkButton(self.pagination_frame, text="Next", width=50, command=self.go_forward)
        self.btn_forward.pack(side="left", padx=5)  # Align to left

        self.btn_end = ctk.CTkButton(self.pagination_frame, text="Last", width=50, command=self.go_to_end)
        self.btn_end.pack(side="left", padx=5)  # Align to left

        # Populate initial data
        self.display_page()
        # print("\nInitial page displayed.")

        # --------------- Crawlers Tab ---------------
        # Dynamically initialize scraper threads and stop events for each scraper
        #TODO:
        #self.meta_data = {name: {"running_time": 0, "total_data": 0, "rate_per_hour": 0, "duplicate_count": 0} for name in scrapers}
        #self.scraper_threads = {name: {"thread": None, "stop_event": None} for name in scrapers}

        # UI for ScrapersTab with dynamic Start/Stop Buttons
        crawlers_tab = self.tabview.add("Scrapers")
        crawlers_label = ctk.CTkLabel(crawlers_tab, text="Scrapers", font=("Arial", 16))
        crawlers_label.pack(anchor="w", padx=10, pady=10)

        # Define button functions
        def start_scraper(scraper_name, scraper_func, start_button, stop_button):
            print(f"Starting {scraper_name}...")
            if not self.scraper_threads[scraper_name]["thread"] or not self.scraper_threads[scraper_name]["thread"].is_alive():
                stop_event = Event()
                thread = Thread(target=self.run_scraper, args=(scraper_func, scraper_name, stop_event))
                self.scraper_threads[scraper_name] = {"thread": thread, "stop_event": stop_event}
                thread.start()
                
                # Update button states
                start_button.configure(state="disabled")
                stop_button.configure(state="normal")

        def stop_scraper(scraper_name, start_button, stop_button):
            print(f"Stopping {scraper_name}...")
            if self.scraper_threads[scraper_name]["stop_event"]:
                self.scraper_threads[scraper_name]["stop_event"].set()
                self.scraper_threads[scraper_name]["thread"].join()
                self.scraper_threads[scraper_name] = {"thread": None, "stop_event": None}
                
                # Update button states
                start_button.configure(state="normal")
                stop_button.configure(state="disabled")

        # Add buttons for each scraper
        # Create UI for each scraper
        self.metadata_labels = {}
        # Inside the loop where you create UI for each scraper
        '''
        for scraper_name, scraper_func in scrapers.items():
            # Frame for each scraper's controls
            scraper_frame = ctk.CTkFrame(crawlers_tab)
            scraper_frame.pack(fill="x", padx=10, pady=10)

            # Initialize the Start and Stop buttons without assigning command yet
            start_button = ctk.CTkButton(
                scraper_frame, text=f"Start {scraper_name}", fg_color="green"
            )
            start_button.pack(side="left", padx=5)

            stop_button = ctk.CTkButton(
                scraper_frame, text=f"Stop {scraper_name}", fg_color="red", state="disabled"
            )
            stop_button.pack(side="left", padx=5)

            # Now assign the commands using lambdas that capture start_button and stop_button correctly
            start_button.configure(
                command=lambda sn=scraper_name, sf=scraper_func, sb=start_button, stp=stop_button: start_scraper(sn, sf, sb, stp)
            )
            stop_button.configure(
                command=lambda sn=scraper_name, sb=start_button, stp=stop_button: stop_scraper(sn, sb, stp)
            )

            # Metadata display
            metadata_label = ctk.CTkLabel(scraper_frame, text=self.get_metadata_text(scraper_name))
            metadata_label.pack(side="left", padx=20)
            self.metadata_labels[scraper_name] = metadata_label
        '''
        
        # --------------- Reports Tab ---------------

        reports_tab = self.tabview.add("Reports")
        reports_label = ctk.CTkLabel(reports_tab, text="Reports", font=("Arial", 16))
        reports_label.pack(anchor="w", padx=10, pady=10)

        for i in range(1, 4):
            reports_button = ctk.CTkButton(reports_tab, text=f"Reports {i}")
            reports_button.pack(anchor="w", padx=10, pady=5)
            # print(f"Crawler button {i} initialized.")

    # --- KEYS

    def get_all_keys(self, lst, sample_size=1000):
        all_keys = set()
        sampled_entries = random.sample(lst, min(sample_size, len(lst)))  # Get a random sample up to 1000 entries
        for entry in sampled_entries:
            all_keys.update(entry.keys())
        return list(all_keys)

        # --------------- SORT RELATED ---------------
    def most_frequent_type(self, lst, key):
        type_counter = Counter()
        
        # Iterate over the first 100 items (or fewer if the list has less than 100 items)
        for entry in lst[:100]:
            if key in entry:
                value = entry[key]
                value_type = type(value).__name__  # Get the type name as a string
                type_counter[value_type] += 1
        
        if type_counter:
            # Return the most common type, but return 'str' if 'NoneType' is the most common
            most_common = type_counter.most_common(1)[0][0]
            return 'str' if most_common == 'NoneType' else most_common
        else:
            return str  # Return str if no types were found
        
    def custom_sort_by_type(self, lst, key, most_frequent_type, reverse=False):
        sorted_list = []
        bad_values = []

        # Separate valid and invalid entries based on the most frequent type
        for entry in lst:
            if key in entry:
                value = entry[key]
                if type(value).__name__ == most_frequent_type:
                    sorted_list.append(entry)
                else:
                    bad_values.append(entry)
            else:
                bad_values.append(entry)

        # Implement a simple sort for the valid entries
        for i in range(len(sorted_list)):
            for j in range(i + 1, len(sorted_list)):
                if (not reverse and sorted_list[i][key] > sorted_list[j][key]) or (reverse and sorted_list[i][key] < sorted_list[j][key]):
                    sorted_list[i], sorted_list[j] = sorted_list[j], sorted_list[i]

        # Append bad values to the end
        sorted_list.extend(bad_values)
        return sorted_list

    def sort_data(self, ordering, key):
        reverse = ordering == "Desc"  # Determine if the sort should be in reverse order

        data_type = self.most_frequent_type(self.data_entries, key)
        print("data_type:", data_type)

        items_sorted = self.custom_sort_by_type(self.data_entries, key, data_type, reverse)
        print("items_sorted:", items_sorted[:10])
        self.data_entries = items_sorted

        self.display_page()  # Refresh the display to show sorted data

    # -- SCRAPER STUF

    # Format the metadata text to display in the UI
    def get_metadata_text(self, scraper_name):
        meta = self.meta_data[scraper_name]
        return (
            f"Running Time: {meta['running_time']:.2f}s | "
            f"Total Data: {meta['total_data']} | "
            f"Rate/Hour: {meta['rate_per_hour']:.2f} | "
            f"Duplicates: {meta['duplicate_count']}"
        )

    # Run each scraper, process, and update metadata
    def run_scraper(self, scraper_func, name, stop_event):
        start_time = datetime.datetime.now()
        data_count = 0
        duplicate_count = 0
        unique_records = set()
        
        try:
            for data_batch in scraper_func(stop_event):
                if stop_event.is_set():
                    break
                
                # Process the data batch
                data_count += len(data_batch)
                for record in data_batch:
                    record_id = tuple(record.items())
                    if record_id in unique_records:
                        duplicate_count += 1
                    else:
                        unique_records.add(record_id)
                
                # Update metadata
                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
                rate_per_hour = data_count / (elapsed_time / 3600) if elapsed_time > 0 else 0
                self.meta_data[name] = {
                    "running_time": elapsed_time,
                    "total_data": data_count,
                    "rate_per_hour": rate_per_hour,
                    "duplicate_count": duplicate_count
                }
                
                # Update the UI for metadata
                self.metadata_labels[name].configure(text=self.get_metadata_text(name))

        except Exception as e:
            print(f"Error in {name}: {e}")
        finally:
            print(f"{name} has stopped.")
            self.metadata_labels[name].configure(text=self.get_metadata_text(name))

    # --------------- Helper Methods for Pagination ---------------

    def get_page_label_text(self, total_entries):
        total_pages = (total_entries - 1) // config.CONFIG['entries_per_page'] + 1
        print(f"Page label updated: {self.current_page + 1} / {total_pages}")
        return f"Page {self.current_page + 1} of {total_pages}"

    def toggle_filter(self, key):
        button = self.filter_buttons[key]
        print(f"Toggling filter '{key}'; Current state: {self.active_filters[key]}")
        
        # Toggle the color and state
        if self.active_filters[key]:
            button.configure(fg_color="gray")
            self.active_filters[key] = False
        else:
            button.configure(fg_color="#1f6aa5")
            self.active_filters[key] = True

        print(f"Filter '{key}' new state: {self.active_filters[key]}")
        self.display_page()

    def display_page(self, query=None):
        # Clear existing widgets in the data frame
        for widget in self.data_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        # Filter data based on the query if provided
        
        if query:
            query_lower = query.lower()  # Convert query to lowercase for case-insensitive comparison
            self.query = query.lower()
            filtered_data = []
            for entry in self.data_entries:
                found = False
                for value in entry.values():
                    if query_lower in str(value).lower():
                        found = True
                        break
                if found:
                    filtered_data.append(entry)
        else:
            # If no query, use all data entries
            self.query = None
            filtered_data = self.data_entries

        # Apply active filters to the filtered data
        self.filtered_data = []  # Store filtered data in an instance variable
        for entry in filtered_data:
            filter_passed = True
            for key, active in self.active_filters.items():
                if active:
                    skippables = [None, "", "N/A", "n/a", "NULL", "null", "-", "--", "unknown", "Unknown", "None"]
                    if entry.get(key) in skippables:
                        filter_passed = False
                        break
            if filter_passed:
                self.filtered_data.append(entry)

        # Calculate pagination based on the filtered data with active filters applied
        total_entries = len(self.filtered_data)
        start_idx = self.current_page * config.CONFIG['entries_per_page']
        end_idx = min(start_idx + config.CONFIG['entries_per_page'], total_entries)

        for idx in range(start_idx, end_idx):
            entry = self.filtered_data[idx]

            # Create a frame to display the entry details
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color="#333333", border_width=2)
            entry_frame.pack(fill="x", padx=10, pady=10)

            # Display each field in the entry
            for field, data in entry.items():

                if field == "root_url":
                    continue
                #if field == "recent_scrape_time":
                #    continue
                elif isinstance(data, str) and re.match(r'^(http|https)://', data):
                    ctk.CTkButton(
                        entry_frame,
                        text="Link",
                        width=100,
                        command=lambda url=data: webbrowser.open(url)
                    ).pack(anchor="w", padx=10, pady=5)
                elif field == "images" and isinstance(data, list):
                    self.create_image_viewer(entry_frame, data)
                else:
                    self.create_toggle_label(entry_frame, field, data)

        # Update the page label to reflect the current page and total entries
        self.page_label.configure(text=self.get_page_label_text(total_entries))

    def create_image_viewer(self, parent, images):
        # Track the current image index
        image_index = 0

        def load_image(index):
            try:
                img_url = images[index]
                response = requests.get(img_url, timeout=10)  # Set a timeout for the request

                # Verify that the response contains image data
                if response.status_code == 200 and 'image' in response.headers['Content-Type']:
                    img_data = Image.open(BytesIO(response.content))
                    img_data.thumbnail((200, 200))  # Resize image to fit thumbnail
                    photo = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(200, 200))
                    image_label.configure(image=photo)
                    image_label.image = photo
                else:
                    raise ValueError("URL did not return a valid image file.")
            
            except requests.RequestException as e:
                print(f"Network error: Unable to load image from URL {img_url} - {e}")
                display_placeholder("Network error")  # Show placeholder for network errors

            except UnidentifiedImageError:
                print(f"Error: Unable to identify image file from URL {img_url}")
                display_placeholder("Invalid image")  # Show placeholder for invalid image data

            except Exception as e:
                print(f"Unexpected error: {e}")

                display_placeholder("Error")  # Show a generic error placeholder

        def display_placeholder(message):
            # Use grid instead of pack for consistent layout management
            placeholder = ctk.CTkLabel(image_label, text=message, font=("Arial", 12))
            placeholder.grid(row=0, column=0, padx=10, pady=10)  # Adjust placement as needed

        # Set up image frame with navigation buttons
        img_frame = ctk.CTkFrame(parent)
        img_frame.pack(fill="x", padx=10, pady=5)

        if len(images) > 1:
            ctk.CTkButton(img_frame, text="<", width=30, command=lambda: scroll_image(-1)).pack(side="left")

        # Initialize the main image label
        image_label = ctk.CTkLabel(img_frame, text="")
        image_label.pack(side="left", padx=10, pady=5)
        load_image(image_index)  # Load the initial image

        if len(images) > 1:
            ctk.CTkButton(img_frame, text=">", width=30, command=lambda: scroll_image(1)).pack(side="right")

        def scroll_image(direction):
            nonlocal image_index
            image_index = (image_index + direction) % len(images)
            load_image(image_index)  # Update to the new image

    def create_toggle_label(self, parent, field, data):
        # Determine if the data can be truncated
        if isinstance(data, (str, list, tuple)):  # Only types that have a length
            is_truncated = len(data) > config.CONFIG['string_max']
            display_text = data[:config.CONFIG['string_max']] + '...' if is_truncated else data
        else:
            is_truncated = False
            display_text = str(data)  # Convert non-truncatable data to string for display

        # Create the row frame
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", padx=10, pady=2)
        
        # Display the truncated or full text in the label
        label = ctk.CTkLabel(row_frame, text=f"{field.capitalize()}: {display_text}", anchor="w", wraplength=450)
        label.pack(side="left", fill="x", expand=True)
        
        # Expanded text label, initially hidden
        expanded_text_label = ctk.CTkLabel(parent, text=f"{field.capitalize()}: {data}", anchor="w", wraplength=450)
        expanded_text_label.pack(anchor="w", padx=10, pady=2)
        expanded_text_label.pack_forget()

        if is_truncated:
            def toggle_text():
                if expanded_text_label.winfo_viewable():
                    expanded_text_label.pack_forget()
                    label.configure(text=f"{field.capitalize()}: {display_text}")
                    toggle_button.configure(text="Show More")
                else:
                    expanded_text_label.pack(anchor="w", padx=10, pady=2)
                    toggle_button.configure(text="Hide")
            
            # Add the toggle button if truncation is enabled
            toggle_button = ctk.CTkButton(row_frame, text="Show More", width=70, command=toggle_text)
            toggle_button.pack(side="right")

    def search_data(self, query):
        print("SEARCH QUERY", query)
        self.display_page(query)

    # Pagination Methods
    def go_to_beginning(self):
        self.current_page = 0
        print("\nNavigating to the beginning")
        
        self.display_page(self.query)

    def go_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            print("\nNavigating to the previous page")
            self.display_page(self.query)

    def go_forward(self):
        # Use the length of filtered data if it exists, otherwise fall back to data_entries
        total_entries = len(self.filtered_data) if hasattr(self, 'filtered_data') else len(self.data_entries)
        max_page = (total_entries - 1) // config.CONFIG['entries_per_page']
        
        if self.current_page < max_page:
            self.current_page += 1
            print("\nNavigating to the next page")
            self.display_page(self.query)

    def go_to_end(self):
        # Use the length of filtered data if it exists, otherwise fall back to data_entries
        total_entries = len(self.filtered_data) if hasattr(self, 'filtered_data') else len(self.data_entries)
        self.current_page = (total_entries - 1) // config.CONFIG['entries_per_page']
        print("\nNavigating to the end")
        self.display_page(self.query)
    

# Run the app with a specific path
if __name__ == "__main__":
    app = GUI(path="./logs/crawl_data.json")
    app.mainloop()