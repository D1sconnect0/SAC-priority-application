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
                    "Business Managment", "Economics", "Legal Studies",
                    "Software Development", "French", "Latin", "Chinese",
                    "Mesic composition", "Health and Human Development",
                    "Physical Education", "Media", "Visual communication design"]
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
        with open("selected_subjects.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(actual_selected_subjects)
        messagebox.showinfo("Success", f"The selected subjects have been saved ({len(actual_selected_subjects)} selected).")
        root.destroy()  # 关闭主窗口
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

# Create the main window
root = tk.Tk()
root.title("Subject Selector")

# Create six dropdown lists
combo1 = ttk.Combobox(root)
combo1.grid(row=0, column=0, padx=10, pady=10)
combo1.bind("<Button-1>", show_subjects)
combo1.set("Select Subject")

combo2 = ttk.Combobox(root)
combo2.grid(row=0, column=1, padx=10, pady=10)
combo2.bind("<Button-1>", show_subjects)
combo2.set("Select Subject")

combo3 = ttk.Combobox(root)
combo3.grid(row=1, column=0, padx=10, pady=10)
combo3.bind("<Button-1>", show_subjects)
combo3.set("Select Subject")

combo4 = ttk.Combobox(root)
combo4.grid(row=1, column=1, padx=10, pady=10)
combo4.bind("<Button-1>", show_subjects)
combo4.set("Select Subject")

combo5 = ttk.Combobox(root)
combo5.grid(row=2, column=0, padx=10, pady=10)
combo5.bind("<Button-1>", show_subjects)
combo5.set("Select Subject")

combo6 = ttk.Combobox(root)
combo6.grid(row=2, column=1, padx=10, pady=10)
combo6.bind("<Button-1>", show_subjects)
combo6.set("Select Subject")

# Create the confirm button
confirm_button = tk.Button(root, text="Confirm Selection", command=confirm_selection)
confirm_button.grid(row=3, column=0, columnspan=2, pady=10)

# Run the main loop
root.mainloop()