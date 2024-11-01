import customtkinter as ctk
import json
import webbrowser
import re
from PIL import Image
import requests
from io import BytesIO

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
        data_tab.grid_columnconfigure(0, weight=3)
        data_tab.grid_columnconfigure(1, weight=1)
        data_tab.grid_rowconfigure(1, weight=1)

        # Header for the Data tab
        label_button_frame = ctk.CTkFrame(data_tab)
        label_button_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        data_label = ctk.CTkLabel(label_button_frame, text="Data", font=("Arial", 16))
        data_label.pack(side="left")
        print("\nData label created.")

        # Download button
        download_button = ctk.CTkButton(label_button_frame, text="Download Data", width=120)
        download_button.pack(side="left", padx=10)
        print("\nDownload button created.")

        # Scrollable frame to display the data entries
        self.data_frame = ctk.CTkScrollableFrame(data_tab)
        self.data_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        # print("\nData scrollable frame created.")

        # Placeholder for filter sidebar
        filter_frame = ctk.CTkFrame(data_tab)
        filter_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Header label for the Filters section
        filter_label = ctk.CTkLabel(filter_frame, text="Filters", font=("Arial", 16))
        filter_label.pack(anchor="w", padx=10, pady=5)
        print("\nFilters section header created.")

        # Store references to buttons and states
        self.filter_buttons = {}
        self.active_filters = {}

        # Initialize filter buttons based on JSON keys
        if self.data_entries:
            json_keys = self.data_entries[0].keys()
            for key in json_keys:
                self.active_filters[key] = False
                
                # Create a toggle button for each key
                toggle_button = ctk.CTkButton(
                    filter_frame,
                    text=f"{key.capitalize()} Filter",
                    width=150,
                    fg_color="gray",
                    command=lambda k=key: self.toggle_filter(k)
                )
                toggle_button.pack(anchor="w", padx=10, pady=2)
                
                # Store the button reference
                self.filter_buttons[key] = toggle_button
                # print(f"Filter button created for '{key}'")

        # --------------- Pagination Controls ---------------

        self.pagination_frame = ctk.CTkFrame(data_tab)
        self.pagination_frame.grid(row=2, column=0, columnspan=2, pady=10)
        print("\nPagination frame created.")

        # Pagination buttons
        self.btn_beginning = ctk.CTkButton(self.pagination_frame, text="<<", width=30, command=self.go_to_beginning)
        self.btn_beginning.pack(side="left", padx=5)

        self.btn_back = ctk.CTkButton(self.pagination_frame, text="<", width=30, command=self.go_back)
        self.btn_back.pack(side="left", padx=5)

        # Page indicator label
        self.page_label = ctk.CTkLabel(self.pagination_frame, text=self.get_page_label_text())
        self.page_label.pack(side="left", padx=5)

        self.btn_forward = ctk.CTkButton(self.pagination_frame, text=">", width=30, command=self.go_forward)
        self.btn_forward.pack(side="left", padx=5)

        self.btn_end = ctk.CTkButton(self.pagination_frame, text=">>", width=30, command=self.go_to_end)
        self.btn_end.pack(side="left", padx=5)
        # print("\nPagination buttons initialized.")

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

    # --------------- Helper Methods for Pagination ---------------

    def get_page_label_text(self):
        total_pages = (len(self.data_entries) - 1) // CONFIG['entries_per_page'] + 1
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

    def display_page(self):
        # print(f"Displaying page {self.current_page + 1}")
        for widget in self.data_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        start_idx = self.current_page * CONFIG['entries_per_page']
        end_idx = min(start_idx + CONFIG['entries_per_page'], len(self.data_entries))
        # print(f"Displaying entries {start_idx} to {end_idx}")

        for idx in range(start_idx, end_idx):
            entry = self.data_entries[idx]
            if not all(entry.get(key) is not None for key, active in self.active_filters.items() if active):
                print(f"Skipping entry {idx} due to active filters")
                continue

            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color="#333333", border_width=2)
            entry_frame.pack(fill="x", padx=10, pady=10)
            # print(f"Entry {idx} displayed.")

            for field, data in entry.items():
                if field == "root_url":
                    continue
                if isinstance(data, str) and re.match(r'^(http|https)://', data):
                    ctk.CTkButton(entry_frame, text=f"{field.capitalize()} Link", width=100,
                                  command=lambda url=data: webbrowser.open(url)).pack(anchor="w", padx=10, pady=5)
                    # print(f"URL link created for '{field}'")
                elif field == "images" and isinstance(data, list):
                    self.create_image_viewer(entry_frame, data)
                    # print(f"Image viewer created for '{field}'")
                else:
                    self.create_toggle_label(entry_frame, field, data)

        self.page_label.configure(text=self.get_page_label_text())

    def create_image_viewer(self, parent, images):
        # print(f"Creating image viewer for {len(images)} images")
        image_index = 0

        def load_image(index):
            img_url = images[index]
            # print(f"Loading image from URL: {img_url}")
            response = requests.get(img_url)
            img_data = Image.open(BytesIO(response.content))
            img_data.thumbnail((200, 200))
            photo = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(200, 200))
            image_label.configure(image=photo)
            image_label.image = photo

        img_frame = ctk.CTkFrame(parent)
        img_frame.pack(fill="x", padx=10, pady=5)
        if len(images) > 1:
            ctk.CTkButton(img_frame, text="<", width=30, command=lambda: scroll_image(-1)).pack(side="left")
        image_label = ctk.CTkLabel(img_frame, text="")
        image_label.pack(side="left", padx=10, pady=5)
        load_image(image_index)
        if len(images) > 1:
            ctk.CTkButton(img_frame, text=">", width=30, command=lambda: scroll_image(1)).pack(side="right")

        def scroll_image(direction):
            nonlocal image_index
            image_index = (image_index + direction) % len(images)
            load_image(image_index)

    def create_toggle_label(self, parent, field, data):
        # print(f"Creating label for field '{field}'")
        is_truncated = len(data) > CONFIG['string_max']
        display_text = data[:CONFIG['string_max']] + '...' if is_truncated else data
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", padx=10, pady=2)
        label = ctk.CTkLabel(row_frame, text=f"{field.capitalize()}: {display_text}", anchor="w", wraplength=450)
        label.pack(side="left", fill="x", expand=True)
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
            toggle_button = ctk.CTkButton(row_frame, text="Show More", width=70, command=toggle_text)
            toggle_button.pack(side="right")

    # Pagination Methods
    def go_to_beginning(self):
        self.current_page = 0
        print("\nNavigating to the beginning")
        self.display_page()

    def go_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            print("\nNavigating to the previous page")
            self.display_page()

    def go_forward(self):
        if self.current_page < (len(self.data_entries) - 1) // CONFIG['entries_per_page']:
            self.current_page += 1
            print("\nNavigating to the next page")
            self.display_page()

    def go_to_end(self):
        self.current_page = (len(self.data_entries) - 1) // CONFIG['entries_per_page']
        print("\nNavigating to the end")
        self.display_page()

# Run the app with a specific path
if __name__ == "__main__":
    app = GUI(path="./demo_data.json")
    app.mainloop()
