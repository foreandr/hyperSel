import customtkinter as ctk

# Sample data with added 'date' field
test_data = [
    {
        "name": "John Doe",
        "location": "Toronto, ON",
        "license_no": "Driver's License",
        "status": "Active",
        "workers_comp": "N/A",
        "date": "2024-01-15"
    },
    {
        "name": "Jane Smith",
        "location": "Vancouver, BC",
        "license_no": None,
        "status": "Pending",
        "workers_comp": "N/A",
        "date": "2024-02-20"
    },
    {
        "name": "Alex Johnson",
        "location": "Calgary, AB",
        "license_no": "Pilot License",
        "status": "Expired",
        "workers_comp": "Valid",
        "date": "2023-11-05"
    },
    {
        "name": "Emily Davis",
        "location": "Montreal, QC",
        "license_no": "Fishing License",
        "status": "Active",
        "workers_comp": "Pending",
        "date": "2024-03-10"
    }
]

# Initialize the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("People Data Viewer")
        self.geometry("600x400")
        
        # Search bar
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, width=400, placeholder_text="Search by name")
        self.search_entry.grid(row=0, column=0, padx=20, pady=10)
        
        self.search_button = ctk.CTkButton(self, text="Search", command=self.search)
        self.search_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Data display
        self.data_frame = ctk.CTkScrollableFrame(self, width=580, height=300)
        self.data_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Load initial data
        self.load_data(test_data)
    
    def load_data(self, data):
        """Clear the data frame and load the data entries."""
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        for entry in data:
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10)
            entry_frame.pack(fill="x", padx=5, pady=5)
            
            name_label = ctk.CTkLabel(entry_frame, text=f"Name: {entry['name']}", font=("Arial", 14, "bold"))
            name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            location_label = ctk.CTkLabel(entry_frame, text=f"Location: {entry['location']}", font=("Arial", 12))
            location_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

            license_label = ctk.CTkLabel(entry_frame, text=f"License: {entry['license_no'] or 'N/A'}", font=("Arial", 12))
            license_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

            status_label = ctk.CTkLabel(entry_frame, text=f"Status: {entry['status']}", font=("Arial", 12))
            status_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

            workers_comp_label = ctk.CTkLabel(entry_frame, text=f"Workers Comp: {entry['workers_comp']}", font=("Arial", 12))
            workers_comp_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

            date_label = ctk.CTkLabel(entry_frame, text=f"Date: {entry['date']}", font=("Arial", 12))
            date_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    def search(self):
        """Filter data based on search input."""
        search_term = self.search_var.get().lower()
        filtered_data = [entry for entry in test_data if search_term in entry["name"].lower()]
        self.load_data(filtered_data)

# Run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
