from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import random
import csv

CSV_FILE = 'lots_and_samples.csv'
FIELDNAMES = ['datetime', 'Lot', 'Serial', 'FullCode', 'Name', 'Notes', 'Active']  # Added 'Active'

try:
    with open(CSV_FILE, 'x', newline='') as f:
        csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()
        csv.DictWriter(f, fieldnames=FIELDNAMES).writerow({'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
except FileExistsError:
    pass

generate_code = lambda length: ''.join([str(random.randint(0, 9)) for _ in range(length)])

class LotSampleApp:
    def __init__(self, root):
        self.root, self.lots, self.samples = root, [], []
        [setattr(self, attr, tk.StringVar()) for attr in ['lot_name', 'sample_name', 'selected_lot', 'selected_sample']]
        self.sample_active = tk.BooleanVar(value=False)


        self.root.title("Lot and Sample Manager")
        self.setup_ui()
        self.load_data()
        self.adjust_window_size()
    @property
    def lot_names(self):
        return [lot['Name'] for lot in self.lots]

    def adjust_window_size(self):
        self.root.update_idletasks()
        current_width = self.root.winfo_width()
        self.root.geometry(f"{round(1.1 * current_width)}x{self.root.winfo_height()}")

    def setup_ui(self):
        self.root.grid_rowconfigure(0, weight=1)  # Add Lot section
        self.root.grid_rowconfigure(1, weight=1)  # Add Sample section
        self.root.grid_rowconfigure(2, weight=2)  # Browse section (made twice as large as others)
        self.root.grid_columnconfigure(0, weight=1)

        # Add Lot section
        add_lot_frame = ttk.LabelFrame(self.root, text="Add Lot")
        add_lot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(add_lot_frame, text="Lot Name:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(add_lot_frame, textvariable=self.lot_name, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(add_lot_frame, text="Generate Lot", command=self.add_lot).grid(row=0, column=2, padx=5, pady=5)

        # Add Sample section
        add_sample_frame = ttk.LabelFrame(self.root, text="Add Sample")
        add_sample_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(add_sample_frame, text="Select Lot:").grid(row=0, column=0, padx=5, pady=5)
        self.lot_combobox = ttk.Combobox(add_sample_frame, values=self.lot_names, textvariable=self.selected_lot, width=60)  # change width to 60
        self.lot_combobox.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_sample_frame, text="Sample Name:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(add_sample_frame, textvariable=self.sample_name, width=60).grid(row=1, column=1, padx=5, pady=5)  # Setting width to 60 (assuming the original width was 20)
        ttk.Button(add_sample_frame, text="Add Sample", command=self.add_sample).grid(row=1, column=2, padx=5, pady=5)

        # New UI for displaying the 12-digit code
        ttk.Label(add_sample_frame, text="Generated Code:").grid(row=2, column=0, padx=5, pady=5)
        self.generated_code_display = ttk.Entry(add_sample_frame, state="readonly", width=60)  # Display bar for the generated code
        self.generated_code_display.grid(row=2, column=1, padx=5, pady=5)

        # Browse Lots and Samples section
        browse_frame = ttk.LabelFrame(self.root, text="Browse Lots and Samples")
        browse_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(browse_frame, text="Select Lot:").grid(row=0, column=0, padx=5, pady=5)
        self.browse_lot_combobox = ttk.Combobox(browse_frame, textvariable=self.selected_lot, state="readonly", postcommand=self.update_sample_dropdown, width=60)  # change width to 60
        self.browse_lot_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Bind the event to the combobox
        self.browse_lot_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_sample_dropdown())

        ttk.Label(browse_frame, text="Select Sample:").grid(row=1, column=0, padx=5, pady=5)
        self.browse_sample_combobox = ttk.Combobox(browse_frame, textvariable=self.selected_sample, state="readonly", width=60)
        self.browse_sample_combobox.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(browse_frame, text="Load", command=self.load_selected_sample).grid(row=1, column=2, padx=5, pady=5)

        # Search bar in Browse section
        ttk.Label(browse_frame, text="Enter Code:").grid(row=3, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(browse_frame)  # Text entry for the search term
        self.search_entry.grid(row=3, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(browse_frame, text="Search", command=self.search_code)
        self.search_button.grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(browse_frame, text="Notes:").grid(row=4, column=0, padx=5, pady=5)
        self.notes_text = tk.Text(browse_frame, width=60, height=10)
        self.notes_text.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        ttk.Checkbutton(browse_frame, text="Active", variable=self.sample_active).grid(row=5, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(browse_frame, text="Save Notes", command=self.save_notes).grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    def search_notes(self):
        search_code = self.search_entry.get().strip()
        print(f"Searching for code: {search_code}")

        if len(search_code) != 12:  # Validate the code length
            messagebox.showerror("Error", "Please enter a valid 12-digit code.")
            return

        # Find the sample that matches the entered code
        corresponding_sample = next((sample for sample in self.samples if sample['FullCode'] == search_code), None)

        if corresponding_sample:
            # If a matching sample is found, display its notes
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(tk.END, corresponding_sample['Notes'])
            print(f"Found sample: {corresponding_sample}")

            messagebox.showinfo("Not Found", "No sample found with the provided code.")

    def add_lot(self):
        lot_name = self.lot_name.get().strip()
        if not lot_name:
            messagebox.showerror("Error", "Lot name cannot be empty.")
            return

        lot_code = generate_code(8)
        lot = {
            'Lot': lot_code,
            'Name': lot_name,
            # Other fields remain empty for a lot entry
        }

        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writerow(lot)

        self.lots.append(lot)
        self.update_lot_dropdown()
        self.lot_name.set('') # Clear the input field

    def find_lot_name_by_lot_number(self, lot_number):
        for lot in self.lots:
            if lot['Lot'] == lot_number:
                return lot['Name']
        return None


    def return_lot_name(self, lot_id):
        with open(CSV_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Lot'] == lot_id and not row['Serial']:
                    return row['Name']
        return None

    def load_data(self):
        self.samples = []
        self.lots = []
        with open(CSV_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Lot'] and not row['Serial']:  # It's a lot
                    self.lots.append(row)
                if row['Serial']:  # It's a sample
                    row['Active'] = row['Active'] == 'True'  # Convert string to boolean
                    self.samples.append(row)
        self.update_lot_dropdown()
        self.load_selected_sample()


    def update_lot_dropdown(self):
        self.lot_combobox['values'] = [lot['Name'] for lot in self.lots]
        self.browse_lot_combobox['values'] = [lot['Name'] for lot in self.lots]

    def add_sample(self):
        sample_name = self.sample_name.get().strip()
        if not sample_name:
            messagebox.showerror("Error", "Sample name cannot be empty.")
            return

        lot_code = next((lot['Lot'] for lot in self.lots if lot['Name'] == self.selected_lot.get()), None)
        if lot_code is None:
            messagebox.showerror("Error", "Selected lot does not exist.")
            return # This should never happen if the UI is consistent with the data

        sample_code = generate_code(4) # Assuming generate_code is a function that generates a random 4-digit code
        full_code = lot_code + sample_code # The full 12-digit code consists of the lot and sample codes

        sample = {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Lot': lot_code,
            'Serial': sample_code,
            'FullCode': full_code,
            'Name': sample_name,
            'Notes': '',
            'Active': 'False', # By default, a new sample is not active
        }
        # Saving the sample to the CSV file
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writerow(sample)

        # Provide the full code for the user (could be used for QR code generation or other identification methods)
        self.generated_code_display.config(state="normal") # Enable writing to the widget
        self.generated_code_display.delete(0, tk.END) # Clear the current content
        self.generated_code_display.insert(0, full_code) # Display the generated code
        self.generated_code_display.config(state="readonly") # Prevent user modification

        self.samples.append(sample) # Add the new sample to the internal list
        self.selected_lot.set('') # Clear the selected lot
        self.sample_name.set('') # Clear the input for the sample name

        # Optionally, you could also update the sample dropdown in the 'Browse Lots and Samples' section
        self.update_sample_dropdown() # Refresh samples dropdown based on the current lot


    def search_code(self):
        code = self.search_entry.get().strip()
        
        if ',' not in code:
            # Direct FullCode search
            matched_sample = next((sample for sample in self.samples if sample['FullCode'] == code), None)
            if matched_sample:
                self.selected_lot.set(self.return_lot_name(matched_sample['Lot']))
                self.selected_sample.set(matched_sample['Name'])
                self.sample_active.set(matched_sample['Active'] == 'True')
                self.load_data()
                return
            else:
                messagebox.showerror("Error", "No data found for the provided FullCode.")
                return
        
        # Extract lot_code from the entered FullCode
        lot_code_from_fullcode = code[:8]  # Assuming the first 8 characters represent the lot_code
        # Search for an entry with this lot_code and without a 4-digit sample ID
        original_lot_entry = next((lot for lot in self.lots if lot['Lot'] == lot_code_from_fullcode and (not lot.get('Serial') or len(lot.get('Serial').strip()) != 4)), None)
        # If such an entry is found, set the dropdown to the Name attribute of this entry
        if original_lot_entry:
            self.browse_lot_combobox.set(original_lot_entry['Name'])
        else:
            self.browse_lot_combobox.set("")
        split_code = code.split(',')
        if len(split_code) < 7:
            messagebox.showerror("Error", "Please check the format of the provided code.")
            return
        
        lot_code, sample_code = split_code[1], split_code[2]
        
        # Search for the lot and sample based on the provided codes
        lot_name = next((lot['Name'] for lot in self.lots if lot['Lot'] == lot_code), None)
        sample_name = next((sample['Name'] for sample in self.samples if sample['Serial'] == sample_code), None)
        
        if lot_name and sample_name:
            # Update the dropdowns
            self.selected_lot.set(lot_name)
            self.selected_sample.set(sample_name)
            
            # Update the active button
            self.sample_active.set(split_code[6].strip() == 'True')
            
            # Automatically press the "load" button
            self.load_data()
        else:
            messagebox.showerror("Error", "No data found for the provided code.")

    def update_sample_dropdown(self):
        selected_lot_name = self.selected_lot.get()
        selected_lot = next((lot for lot in self.lots if lot['Name'] == selected_lot_name), None)

        if not selected_lot:
            self.browse_sample_combobox['values'] = []  # Clear the dropdown if no lot is selected
            return

        # Filter samples based on the selected lot
        related_samples = [sample for sample in self.samples if sample['Lot'] == selected_lot['Lot']]
        self.browse_sample_combobox['values'] = [sample['Name'] for sample in related_samples]

        # If there are related samples, set the first one as the default selected value
        if related_samples:
            self.browse_sample_combobox.set(related_samples[0]['Name'])
        else:
            self.browse_sample_combobox.set('')  # Clear the selection if no related samples

    def load_selected_sample(self):
        lot_code = next((lot['Lot'] for lot in self.lots if lot['Name'] == self.selected_lot.get()), None)
        sample_name = self.selected_sample.get()

        if not lot_code or not sample_name:
            return  # Proper error handling/message should be here

        selected_sample = next((sample for sample in self.samples if sample['Name'] == sample_name and sample['Lot'] == lot_code), None)

        if selected_sample:
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(tk.END, selected_sample['Notes'])
            self.sample_active.set(selected_sample['Active'] == 'True')  # Update the Checkbutton's state based on the sample's 'Active' status
            self.sample_active.set(selected_sample['Active'])

    def save_notes(self):
            new_notes = self.notes_text.get(1.0, tk.END).strip()
            search_code = self.search_entry.get().strip()
            selected_sample = None

            # Create a flag to track if any sample is updated
            sample_updated = False

            # Check if a 12-digit code is entered in the search bar
            if len(search_code) == 12:
                # Find the sample that matches the entered code
                selected_sample = next((sample for sample in self.samples if sample['FullCode'] == search_code), None)
                if selected_sample:
                    selected_sample['Notes'] = new_notes  # Update the notes in memory
                    sample_updated = True
            else:
                lot_code = next((lot['Lot'] for lot in self.lots if lot['Name'] == self.selected_lot.get()), None)
                sample_name = self.selected_sample.get()
                selected_sample = next((sample for sample in self.samples if sample['Name'] == sample_name and sample['Lot'] == lot_code), None)
                if selected_sample:
                    selected_sample['Notes'] = new_notes  # Update the notes in memory
                    sample_updated = True

            # Update the active status in memory based on the Checkbutton's state
            if selected_sample:
                selected_sample['Active'] = 'True' if self.sample_active.get() else 'False'
            
            # Now, save the updated data back to the CSV file
            if sample_updated:
                with open(CSV_FILE, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                    writer.writeheader()  # Write the headers first
                    # Write the lots
                    for lot in self.lots:
                        
                        writer.writerow(lot)
                    # Write the samples
                    for sample in self.samples:
                        
                        writer.writerow(sample)

# Run the application
root = tk.Tk()
app = LotSampleApp(root)
root.mainloop()
