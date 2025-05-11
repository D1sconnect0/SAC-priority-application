import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime  # Although not directly used in this version, importing it is a good habit

def show_subjects(event):
    """Updates the dropdown list options when the selection box is clicked."""
    combobox = event.widget
    if combobox == combo1:
        subjects = ["English", "Literature"]
    else:
        subjects = ["General Mathematics", "Method Mathematics", "Specialist Mathematics",
                    "Biology", "Chemistry", "Physics", "Psychology", "History Revolutions",
                    "Modern History", "Politics", "Sociology", "Accounting",
                    "Business Management", "Economics", "Legal Studies",
                    "Software Development", "French", "Latin", "Chinese",
                    "Music Composition", "Health and Human Development",
                    "Physical Education", "Media", "Visual Communication Design"]
    combobox['values'] = subjects

def confirm_selection():
    """Gets the selected subjects and writes them to a CSV file, ignoring 'Select Subject' and closes the window."""
    selected_subjects_with_placeholder = [combo1.get(), combo2.get(), combo3.get(),
                                         combo4.get(), combo5.get(), combo6.get()]
    actual_selected_subjects = [subject for subject in selected_subjects_with_placeholder if subject != "Select Subject"]

    print("Selected subjects (with placeholder):", selected_subjects_with_placeholder)
    print("Actual selected subjects:", actual_selected_subjects)

    if not actual_selected_subjects:
        messagebox.showwarning("Warning", "Please select at least one subject.")
        return

    try:
        with open("programs/selected_subjects.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(actual_selected_subjects)
        messagebox.showinfo("Success", f"The selected subjects have been saved ({len(actual_selected_subjects)} selected).")
        root.destroy()  # Close the main window
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

# Create the main window
root = tk.Tk()
root.title("Subject Selection")

# Configure style for better look and feel
style = ttk.Style(root)
style.theme_use('clam')  # Or try 'alt', 'default', 'classic'

# Set a larger default size for the window
window_width = 240  # Increased width
window_height = 300 # Increased height
root.geometry(f"{window_width}x{window_height}")

# Improved layout using LabelFrames for better grouping
group1 = ttk.LabelFrame(root, text="Select Subjects (Optional)")
group1.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
group1.columnconfigure(0, weight=1)
group1.columnconfigure(1, weight=1)

# Create six dropdown lists with more descriptive labels
ttk.Label(group1, text="English:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
combo1 = ttk.Combobox(group1)
combo1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
combo1.bind("<Button-1>", show_subjects)
combo1.set("Select Subject")

ttk.Label(group1, text="Subject 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
combo2 = ttk.Combobox(group1)
combo2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
combo2.bind("<Button-1>", show_subjects)
combo2.set("Select Subject")

ttk.Label(group1, text="Subject 3:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
combo3 = ttk.Combobox(group1)
combo3.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
combo3.bind("<Button-1>", show_subjects)
combo3.set("Select Subject")

ttk.Label(group1, text="Subject 4:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
combo4 = ttk.Combobox(group1)
combo4.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
combo4.bind("<Button-1>", show_subjects)
combo4.set("Select Subject")

ttk.Label(group1, text="Subject 5:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
combo5 = ttk.Combobox(group1)
combo5.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
combo5.bind("<Button-1>", show_subjects)
combo5.set("Select Subject")

ttk.Label(group1, text="Subject 6:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
combo6 = ttk.Combobox(group1)
combo6.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
combo6.bind("<Button-1>", show_subjects)
combo6.set("Select Subject")

# Create the confirm button with improved styling
confirm_button = ttk.Button(root, text="Confirm Selection", command=confirm_selection)
confirm_button.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

# Center the window on the screen (using the new dimensions)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - window_width) / 2)
y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Run the main loop
root.mainloop()
