import tkinter as tk
from tkinter import ttk
import csv
import os

# Initialize Tkinter window
root = tk.Tk()
root.title("Lot and Sample Management")

# Initialize data storage (CSV filenames)
lot_csv = 'lots.csv'
sample_csv = 'samples.csv'

# Function to save data to CSV
def save_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Function to load data from CSV
def load_from_csv(filename):
    if not os.path.exists(filename):
        return []
    
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        return [row for row in reader]

# Initialize lot and sample data from CSV files
lots = load_from_csv(lot_csv)
samples = load_from_csv(sample_csv)

# Function to add lot
def add_lot():
    lot_id = lot_id_entry.get()
    lot_name = lot_name_entry.get()
    lot_notes = lot_notes_entry.get()
    save_to_csv(lot_csv, [lot_id, lot_name, lot_notes])
    lots.append([lot_id, lot_name, lot_notes])
    lot_id_entry.delete(0, 'end')
    lot_name_entry.delete(0, 'end')
    lot_notes_entry.delete(0, 'end')
    update_lot_dropdown()

# Function to add sample
def add_sample():
    sample_id = sample_id_entry.get()
    sample_name = sample_name_entry.get()
    sample_desc = sample_desc_entry.get()
    associated_lot = associated_lot_dropdown.get()
    save_to_csv(sample_csv, [sample_id, sample_name, sample_desc, associated_lot])
    samples.append([sample_id, sample_name, sample_desc, associated_lot])
    sample_id_entry.delete(0, 'end')
    sample_name_entry.delete(0, 'end')
    sample_desc_entry.delete(0, 'end')
    update_sample_dropdown()

# Function to populate lot dropdown
def update_lot_dropdown():
    lot_dropdown['values'] = [lot[1] for lot in lots]
    associated_lot_dropdown['values'] = [lot[1] for lot in lots]

# Function to populate sample dropdown based on selected lot
def update_sample_dropdown():
    selected_lot = lot_dropdown.get()
    relevant_samples = [sample[1] for sample in samples if sample[3] == selected_lot]
    sample_dropdown['values'] = relevant_samples

# Function to load notes and observations for selected sample
def load_notes():
    selected_lot = lot_dropdown.get()
    selected_sample = sample_dropdown.get()
    for sample in samples:
        if sample[1] == selected_sample and sample[3] == selected_lot:
            notes_text.delete(1.0, 'end')
            notes_text.insert(1.0, sample[2])
            return

# Function to save edited notes
def save_edited_notes():
    selected_lot = lot_dropdown.get()
    selected_sample = sample_dropdown.get()
    for sample in samples:
        if sample[1] == selected_sample and sample[3] == selected_lot:
            sample[2] = notes_text.get(1.0, 'end').strip()
            with open(sample_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(samples)

# Add Lot section
add_lot_frame = ttk.LabelFrame(root, text="Add Lot")
add_lot_frame.grid(row=0, column=0, padx=10, pady=10)

lot_id_entry = ttk.Entry(add_lot_frame, width=30)
lot_id_entry.grid(row=0, column=1)
ttk.Label(add_lot_frame, text="Lot ID:").grid(row=0, column=0)

lot_name_entry = ttk.Entry(add_lot_frame, width=30)
lot_name_entry.grid(row=1, column=1)
ttk.Label(add_lot_frame, text="Lot Name:").grid(row=1, column=0)

lot_notes_entry = ttk.Entry(add_lot_frame, width=30)
lot_notes_entry.grid(row=2, column=1)
ttk.Label(add_lot_frame, text="Notes:").grid(row=2, column=0)

ttk.Button(add_lot_frame, text="Add Lot", command=add_lot).grid(row=3, columnspan=2)

# Add Sample section
add_sample_frame = ttk.LabelFrame(root, text="Add Sample")
add_sample_frame.grid(row=0, column=1, padx=10, pady=10)

sample_id_entry = ttk.Entry(add_sample_frame, width=30)
sample_id_entry.grid(row=0, column=1)
ttk.Label(add_sample_frame, text="Sample ID:").grid(row=0, column=0)

sample_name_entry = ttk.Entry(add_sample_frame, width=30)
sample_name_entry.grid(row=1, column=1)
ttk.Label(add_sample_frame, text="Sample Name:").grid(row=1, column=0)

sample_desc_entry = ttk.Entry(add_sample_frame, width=30)
sample_desc_entry.grid(row=2, column=1)
ttk.Label(add_sample_frame, text="Description:").grid(row=2, column=0)

associated_lot_dropdown = ttk.Combobox(add_sample_frame, values=[lot[1] for lot in lots], width=27)
associated_lot_dropdown.grid(row=3, column=1)
ttk.Label(add_sample_frame, text="Associated Lot:").grid(row=3, column=0)

ttk.Button(add_sample_frame, text="Add Sample", command=add_sample).grid(row=4, columnspan=2)

# Browse Lots and Samples section
browse_frame = ttk.LabelFrame(root, text="Browse Lots and Samples")
browse_frame.grid(row=1, columnspan=2, padx=10, pady=10)

lot_dropdown = ttk.Combobox(browse_frame, values=[lot[1] for lot in lots], width=27)
lot_dropdown.grid(row=0, column=1)
ttk.Label(browse_frame, text="Select Lot:").grid(row=0, column=0)
ttk.Button(browse_frame, text="Load", command=update_sample_dropdown).grid(row=0, column=2)

sample_dropdown = ttk.Combobox(browse_frame, width=27)
sample_dropdown.grid(row=1, column=1)
ttk.Label(browse_frame, text="Select Sample:").grid(row=1, column=0)
ttk.Button(browse_frame, text="Load", command=load_notes).grid(row=1, column=2)

# Notes and Observations
notes_text = tk.Text(browse_frame, height=10, width=40)
notes_text.grid(row=2, columnspan=3)
ttk.Button(browse_frame, text="Save Edited Notes", command=save_edited_notes).grid(row=3, columnspan=3)

# Initialize dropdowns
update_lot_dropdown()

root.mainloop()
