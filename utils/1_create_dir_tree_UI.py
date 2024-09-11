import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to trigger the process
def run_process():
    main_dir = main_dir_entry.get()

    # Check if main_dir is provided
    if not main_dir:
        messagebox.showerror("Error", "--main-dir is required")
        return
    
    # Check if main_dir exists
    if not os.path.isdir(main_dir):
        messagebox.showerror("Error", f"main_dir does not exist: {main_dir}")
        return

    # Define other directories based on main_dir
    input_dir = os.path.join(main_dir, "data/input")
    output_dir = os.path.join(main_dir, "data/output")
    logs_dir = os.path.join(main_dir, "logs")
    backup_dir = os.path.join(logs_dir, "io/backups")
    sample_sheet_dir = os.path.join(logs_dir, "io")
    input_dir_conv = os.path.join(input_dir, "image_conversion")
    output_dir_conv = os.path.join(output_dir, "image_conversion")
    input_dir_reg = os.path.join(input_dir, "image_registration")
    output_dir_reg = os.path.join(output_dir, "image_registration")
    mappings_dir = os.path.join(main_dir, "data/mappings")
    registered_crops_dir = os.path.join(main_dir, "data/registered_crops")

    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(sample_sheet_dir, exist_ok=True)
    os.makedirs(input_dir_conv, exist_ok=True)
    os.makedirs(output_dir_conv, exist_ok=True)
    os.makedirs(input_dir_reg, exist_ok=True)
    os.makedirs(output_dir_reg, exist_ok=True)
    os.makedirs(mappings_dir, exist_ok=True)
    os.makedirs(registered_crops_dir, exist_ok=True)

    # Show success message
    messagebox.showinfo("Success", "Directories have been created and verified.")

# Function to select main directory
def select_main_dir():
    dir_path = filedialog.askdirectory()
    if dir_path:
        main_dir_entry.delete(0, tk.END)
        main_dir_entry.insert(0, dir_path)

# Create the main window
root = tk.Tk()
root.title("Directory Creator")

# Labels and input fields
tk.Label(root, text="Main Directory").grid(row=0, column=0, sticky="e")
main_dir_entry = tk.Entry(root, width=50)
main_dir_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_main_dir).grid(row=0, column=2)

# Run button
tk.Button(root, text="Run", command=run_process, bg="green", fg="white").grid(row=1, column=0, columnspan=3, pady=20)

# Start the main loop
root.mainloop()
