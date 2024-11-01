import customtkinter as ctk
import json
import webbrowser
import re
from PIL import Image
from PIL import UnidentifiedImageError
import requests
from io import BytesIO
import datetime

# Initialize the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG = {
    'string_max': 40,
    'entries_per_page': 8  # Number of entries to display per page
}

class GUI(ctk.CTk):
    
    # --------------- Initialization and Main Window Setup ---------------
    
    def __init__(self, path="./logs/crawl_data.json"):
        super().__init__()
        self.title("Hypersel")
        self.after(100, lambda: self.state("zoomed"))

        # Track the current page index
        self.current_page = 0
        # print("\nApplication initialized.")

        # Load data from the specified path
        with open(path, 'r') as file:
            self.data_entries = json.load(file)
        # print(f"Loaded {len(self.data_entries)} entries from {path}")

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
            json_keys = self.data_entries[0].keys()
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
        crawlers_tab = self.tabview.add("Crawlers")
        crawlers_label = ctk.CTkLabel(crawlers_tab, text="Crawlers", font=("Arial", 16))
        crawlers_label.pack(anchor="w", padx=10, pady=10)

        for i in range(1, 4):
            crawler_button = ctk.CTkButton(crawlers_tab, text=f"Crawler {i}")
            crawler_button.pack(anchor="w", padx=10, pady=5)
            # print(f"Crawler button {i} initialized.")

        # --------------- Reports Tab ---------------

        reports_tab = self.tabview.add("Reports")
        reports_label = ctk.CTkLabel(reports_tab, text="Reports", font=("Arial", 16))
        reports_label.pack(anchor="w", padx=10, pady=10)

        for i in range(1, 4):
            reports_button = ctk.CTkButton(reports_tab, text=f"Reports {i}")
            reports_button.pack(anchor="w", padx=10, pady=5)
            # print(f"Crawler button {i} initialized.")

    # --------------- SORT RELATED ---------------

    def sort_data(self, ordering, key):
        print("ORDERING:", ordering)
        print("key:", key)
        reverse = ordering == "Desc"
        print("reverse:", reverse)
        print("----")

        # Define a helper function for type-specific sorting, handling None values
        def get_sort_key(entry):
            value = entry.get(key, None)

            if value is None:
                return float('inf') if reverse else float('-inf')  # Places None values at the end or beginning based on sorting order

            # Handle different data types
            if isinstance(value, str):
                # Try to parse as date if it's a date string
                try:
                    return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return value.lower()  # Sort case-insensitively for strings

            elif isinstance(value, bool):
                return value  # Boolean sorts False before True by default

            elif isinstance(value, (int, float)):
                return value  # Numbers are sortable directly

            elif isinstance(value, list):
                # Sort lists by length (customizable depending on requirements)
                return len(value)

            elif isinstance(value, dict):
                # Sort dictionaries by the number of keys (customizable)
                return len(value.keys())

            else:
                return value  # Fallback for any other type

        # Sort data entries by the determined key
        self.data_entries.sort(key=get_sort_key, reverse=reverse)
        self.display_page()  # Refresh the display to show sorted data

    # --------------- Helper Methods for Pagination ---------------

    def get_page_label_text(self, total_entries):
        total_pages = (total_entries - 1) // CONFIG['entries_per_page'] + 1
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
        start_idx = self.current_page * CONFIG['entries_per_page']
        end_idx = min(start_idx + CONFIG['entries_per_page'], total_entries)

        for idx in range(start_idx, end_idx):
            entry = self.filtered_data[idx]

            # Create a frame to display the entry details
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color="#333333", border_width=2)
            entry_frame.pack(fill="x", padx=10, pady=10)

            # Display each field in the entry
            for field, data in entry.items():
                if field == "root_url":
                    continue
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
            is_truncated = len(data) > CONFIG['string_max']
            display_text = data[:CONFIG['string_max']] + '...' if is_truncated else data
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
        max_page = (total_entries - 1) // CONFIG['entries_per_page']
        
        if self.current_page < max_page:
            self.current_page += 1
            print("\nNavigating to the next page")
            self.display_page(self.query)

    def go_to_end(self):
        # Use the length of filtered data if it exists, otherwise fall back to data_entries
        total_entries = len(self.filtered_data) if hasattr(self, 'filtered_data') else len(self.data_entries)
        self.current_page = (total_entries - 1) // CONFIG['entries_per_page']
        print("\nNavigating to the end")
        self.display_page(self.query)
    
# Run the app with a specific path
if __name__ == "__main__":
    app = GUI(path="./demo_data1.json")
    app.mainloop()
