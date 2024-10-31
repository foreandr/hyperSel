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
    'entries_per_page': 89  # Number of entries to display per page
}

class GUI(ctk.CTk):
    
    # --------------- Initialization and Main Window Setup ---------------
    
    def __init__(self, path="./logs/crawl_data.json"):
        super().__init__()
        self.title("Hypersel")
        self.after(100, lambda: self.state("zoomed"))

        # Track the current page index
        self.current_page = 0

        # Load data from the specified path
        with open(path, 'r') as file:
            self.data_entries = json.load(file)

        # Set up the main tab view containing "Data" and "Crawlers" tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)  # Padding added for prominence

        # --------------- Data Tab and Content ---------------
        
        data_tab = self.tabview.add("Data")  # Add "Data" tab to the main tab view
        
        # Grid configuration for Data tab layout
        data_tab.grid_columnconfigure(0, weight=3)  # Main content column
        data_tab.grid_columnconfigure(1, weight=1)  # Filter column
        data_tab.grid_rowconfigure(1, weight=1)     # Content row

        # Header for the Data tab
        label_button_frame = ctk.CTkFrame(data_tab)
        label_button_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        data_label = ctk.CTkLabel(label_button_frame, text="Data", font=("Arial", 16))
        data_label.pack(side="left")

        # Download button
        download_button = ctk.CTkButton(label_button_frame, text="Download Data", width=120)
        download_button.pack(side="left", padx=10)

        # Scrollable frame to display the data entries
        self.data_frame = ctk.CTkScrollableFrame(data_tab)
        self.data_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")

        # Placeholder for filter sidebar
        filter_frame = ctk.CTkFrame(data_tab)
        filter_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Header label for the Filters section
        filter_label = ctk.CTkLabel(filter_frame, text="Filters", font=("Arial", 16))
        filter_label.pack(anchor="w", padx=10, pady=5)

        # Placeholder filter labels (Add actual functionality as needed)
        for key in ["Title", "Description", "Date", "Author"]:  # Example filters
            placeholder_filter = ctk.CTkLabel(filter_frame, text=f"{key} Filter", anchor="w")
            placeholder_filter.pack(anchor="w", padx=10, pady=2)

        # --------------- Pagination Controls ---------------

        # Frame for pagination buttons
        self.pagination_frame = ctk.CTkFrame(data_tab)
        self.pagination_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Pagination buttons for navigating through pages
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

        # Populate initial data
        self.display_page()

        # --------------- Crawlers Tab ---------------

        crawlers_tab = self.tabview.add("Crawlers")  # Add "Crawlers" tab to the main tab view
        
        crawlers_label = ctk.CTkLabel(crawlers_tab, text="Crawlers", font=("Arial", 16))
        crawlers_label.pack(anchor="w", padx=10, pady=10)

        # Placeholder buttons for Crawler functionality
        for i in range(1, 4):
            crawler_button = ctk.CTkButton(crawlers_tab, text=f"Crawler {i}")
            crawler_button.pack(anchor="w", padx=10, pady=5)

    # --------------- Helper Methods for Pagination ---------------

    def get_page_label_text(self):
        """Returns the current page label text in the format 'Page X of Y'."""
        total_pages = (len(self.data_entries) - 1) // CONFIG['entries_per_page'] + 1
        return f"Page {self.current_page + 1} of {total_pages}"

    def display_page(self):
        """Displays entries for the current page."""
        # Clear existing widgets in the data frame
        for widget in self.data_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        # Calculate start and end indices for entries
        start_idx = self.current_page * CONFIG['entries_per_page']
        end_idx = min(start_idx + CONFIG['entries_per_page'], len(self.data_entries))
        url_pattern = re.compile(r'^(http|https)://')  # Pattern to identify URLs

        # Display each entry
        for idx in range(start_idx, end_idx):
            entry = self.data_entries[idx]
            background_color = "#333333"

            # Frame for each entry with a border
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color=background_color, border_width=2, border_color="#555555")
            entry_frame.pack(fill="x", padx=10, pady=10)

            # Display fields in the entry
            for field, data in entry.items():
                if field == "root_url":
                    continue  # Skip root_url field
                
                if isinstance(data, str) and url_pattern.match(data):  # Display URLs as links
                    link_button = ctk.CTkButton(
                        entry_frame, text=f"{field.capitalize()} Link", width=100,
                        command=lambda url=data: webbrowser.open(url)
                    )
                    link_button.pack(anchor="w", padx=10, pady=5)
                elif field == "images" and isinstance(data, list) and data:  # Display images
                    self.create_image_viewer(entry_frame, data)
                else:
                    self.create_toggle_label(entry_frame, field, data)

        # Update page label
        self.page_label.configure(text=self.get_page_label_text())

    # --------------- Image Viewer for Displaying Images ---------------

    def create_image_viewer(self, parent, images):
        """Creates an image viewer with scroll arrows if multiple images are present."""
        image_index = 0

        def load_image(index):
            """Helper to load and display an image from URL at a specific index."""
            img_url = images[index]
            response = requests.get(img_url)
            img_data = Image.open(BytesIO(response.content))
            img_data.thumbnail((200, 200))
            photo = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(200, 200))
            image_label.configure(image=photo)
            image_label.image = photo

        # Frame to hold image and navigation buttons
        img_frame = ctk.CTkFrame(parent)
        img_frame.pack(fill="x", padx=10, pady=5)

        # Left arrow button for scrolling images
        if len(images) > 1:
            left_arrow = ctk.CTkButton(img_frame, text="<", width=30, command=lambda: scroll_image(-1))
            left_arrow.pack(side="left")

        # Label to display the image
        image_label = ctk.CTkLabel(img_frame, text="")
        image_label.pack(side="left", padx=10, pady=5)
        load_image(image_index)

        # Right arrow button for scrolling images
        if len(images) > 1:
            right_arrow = ctk.CTkButton(img_frame, text=">", width=30, command=lambda: scroll_image(1))
            right_arrow.pack(side="right")

        def scroll_image(direction):
            """Scroll through images in the list."""
            nonlocal image_index
            image_index = (image_index + direction) % len(images)
            load_image(image_index)

    # --------------- Toggle Label for Showing Full Text on Click ---------------

    def create_toggle_label(self, parent, field, data):
        """Creates a label with a toggle button on the same row, ensuring it wraps within the column."""
        is_truncated = len(data) > CONFIG['string_max']
        display_text = data[:CONFIG['string_max']] + '...' if is_truncated else data

        # Frame to hold the label and the toggle button in the same row
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", padx=10, pady=2)

        # Label with initial display text
        label = ctk.CTkLabel(row_frame, text=f"{field.capitalize()}: {display_text}", anchor="w", wraplength=450)
        label.pack(side="left", fill="x", expand=True)

        # Frame to show additional text when expanded
        expanded_text_label = ctk.CTkLabel(parent, text=f"{field.capitalize()}: {data}", anchor="w", wraplength=450)
        expanded_text_label.pack(anchor="w", padx=10, pady=2)
        expanded_text_label.pack_forget()

        if is_truncated:
            def toggle_text():
                """Toggles between truncated and expanded text display."""
                if expanded_text_label.winfo_viewable():
                    expanded_text_label.pack_forget()
                    label.configure(text=f"{field.capitalize()}: {display_text}")
                    toggle_button.configure(text="Show More")
                else:
                    expanded_text_label.pack(anchor="w", padx=10, pady=2)
                    toggle_button.configure(text="Hide")

            # Toggle button to expand/collapse text
            toggle_button = ctk.CTkButton(row_frame, text="Show More", width=70, command=toggle_text)
            toggle_button.pack(side="right")

    # --------------- Pagination Methods ---------------

    def go_to_beginning(self):
        """Go to the first page."""
        self.current_page = 0
        self.display_page()

    def go_back(self):
        """Go to the previous page if not at the beginning."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def go_forward(self):
        """Go to the next page if not at the end."""
        if self.current_page < (len(self.data_entries) - 1) // CONFIG['entries_per_page']:
            self.current_page += 1
            self.display_page()

    def go_to_end(self):
        """Go to the last page."""
        self.current_page = (len(self.data_entries) - 1) // CONFIG['entries_per_page']
        self.display_page()

# Run the app with a specific path
if __name__ == "__main__":
    # Default path or pass a different path like "./demo_data.json" when initializing App
    app = GUI(path="./demo_data.json")
    app.mainloop()
