import customtkinter as ctk
import json
import webbrowser
import re

# Initialize the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG = {
    'string_max': 40,
    'entries_per_page': 5  # Number of entries to display per page
}

class App(ctk.CTk):
    def __init__(self, path="./logs/crawl_data.json"):
        super().__init__()
        self.title("Dynamic Column Viewer")
        self.geometry("1450x700")  # Default window size, resizable
        self.current_page = 0  # Track the current page index

        # Load data from the specified path
        with open(path, 'r') as file:
            self.data_entries = json.load(file)

        # Configure grid to dynamically resize with window adjustments
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)  # Columns adjust to fill width
        self.grid_rowconfigure(0, weight=1)         # Row adjusts to fill height

        # Data column with scrollable content
        self.data_frame = ctk.CTkScrollableFrame(self)
        self.data_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        data_label = ctk.CTkLabel(self.data_frame, text="Data", font=("Arial", 16))
        data_label.pack(anchor="w", padx=10, pady=5)

        # Filters and Crawlers columns without scrollable content
        for i, column_name in enumerate(["Filters", "Crawlers"], start=1):
            frame = ctk.CTkFrame(self)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            label = ctk.CTkLabel(frame, text=column_name, font=("Arial", 16))
            label.pack(anchor="w", padx=10, pady=5)

        # Pagination controls directly under the Data column
        self.pagination_frame = ctk.CTkFrame(self)
        self.pagination_frame.grid(row=1, column=0, pady=10)
        
        # Small pagination buttons
        self.btn_beginning = ctk.CTkButton(self.pagination_frame, text="<<", width=30, command=self.go_to_beginning)
        self.btn_beginning.pack(side="left", padx=5)
        
        self.btn_back = ctk.CTkButton(self.pagination_frame, text="<", width=30, command=self.go_back)
        self.btn_back.pack(side="left", padx=5)
        
        # Page label with "Page X of Y" format
        self.page_label = ctk.CTkLabel(self.pagination_frame, text=self.get_page_label_text())
        self.page_label.pack(side="left", padx=5)
        
        self.btn_forward = ctk.CTkButton(self.pagination_frame, text=">", width=30, command=self.go_forward)
        self.btn_forward.pack(side="left", padx=5)
        
        self.btn_end = ctk.CTkButton(self.pagination_frame, text=">>", width=30, command=self.go_to_end)
        self.btn_end.pack(side="left", padx=5)

        # Populate initial data
        self.display_page()

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

        # Calculate the start and end indices for entries to display
        start_idx = self.current_page * CONFIG['entries_per_page']
        end_idx = min(start_idx + CONFIG['entries_per_page'], len(self.data_entries))
        url_pattern = re.compile(r'^(http|https)://')  # Pattern to identify URLs

        for idx in range(start_idx, end_idx):
            entry = self.data_entries[idx]
            background_color = "#333333" if idx % 2 == 0 else "#444444"  # Alternate colors

            # Frame for each entry with background color
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color=background_color)
            entry_frame.pack(fill="x", padx=5, pady=5)  # Full width within Data column

            # Display each field in the entry
            for field, data in entry.items():
                if isinstance(data, str) and url_pattern.match(data):  # Check if the field is a URL
                    link_button = ctk.CTkButton(
                        entry_frame, text=f"{field.capitalize()} Link", width=100,
                        command=lambda url=data: webbrowser.open(url)
                    )
                    link_button.pack(anchor="w", padx=10, pady=5)
                else:
                    self.create_toggle_label(entry_frame, field, data)

        # Update page label to reflect the current page and total pages
        self.page_label.configure(text=self.get_page_label_text())

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

        # Frame to show additional text below when expanded
        expanded_text_label = ctk.CTkLabel(parent, text=f"{field.capitalize()}: {data}", anchor="w", wraplength=450)
        expanded_text_label.pack(anchor="w", padx=10, pady=2)
        expanded_text_label.pack_forget()  # Hide initially

        if is_truncated:
            def toggle_text():
                """Toggles between truncated and expanded text display."""
                if expanded_text_label.winfo_viewable():
                    expanded_text_label.pack_forget()  # Hide the expanded text
                    label.configure(text=f"{field.capitalize()}: {display_text}")
                    toggle_button.configure(text="Show More")
                else:
                    expanded_text_label.pack(anchor="w", padx=10, pady=2)  # Show expanded text below
                    toggle_button.configure(text="Hide")

            # Button to toggle expanded view, aligned to the right of the label
            toggle_button = ctk.CTkButton(row_frame, text="Show More", width=70, command=toggle_text)
            toggle_button.pack(side="right")  # Align to the right within the row

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
    app = App(path="./demo_data.json")
    app.mainloop()
