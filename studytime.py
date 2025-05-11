import csv
import tkinter as tk
from tkinter import ttk, messagebox

class StudyTimeApp(tk.Tk):
    def __init__(self, csv_path="studytime.csv"):
        super().__init__()
        self.title("📚 Study Time Tracker")
        self.geometry("500x400")
        self.configure(bg="#f0f4f8")  # light background
        self.csv_path = csv_path

        # Set up styles
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(
            'Treeview',
            background='#ffffff',
            foreground='#333333',
            rowheight=25,
            fieldbackground='#ffffff',
            font=('Helvetica', 10)
        )
        style.map('Treeview', background=[('selected', '#aed6f1')])
        style.configure('Treeview.Heading', font=('Helvetica', 11, 'bold'), background='#d6eaf8')

        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(main_frame, text="Individual Study Sessions", font=('Helvetica', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 5))

        # Treeview setup with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("#1",), show="headings", height=10)
        self.tree.heading("#1", text="Study Time (hrs:mins)")
        self.tree.column("#1", anchor=tk.CENTER, width=150)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Separator
        sep = ttk.Separator(main_frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=10)

        # Total frame
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X)

        self.total_label = ttk.Label(total_frame, text="Total Study Time: 0 hrs 0 mins", font=('Helvetica', 12, 'bold'))
        self.total_label.pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = ttk.Button(total_frame, text="Refresh", command=self.load_and_display_data)
        refresh_btn.pack(side=tk.RIGHT)

        # Load data on start
        self.load_and_display_data()

    def load_and_display_data(self):
        """Read the CSV, populate the tree, and compute total."""
        try:
            with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Clear existing rows
                for row in self.tree.get_children():
                    self.tree.delete(row)

                total_minutes = 0
                for row in reader:
                    try:
                        t = float(row.get("time", 0))
                    except ValueError:
                        continue
                    
                    # Convert time from hours to minutes
                    minutes = int(t * 60)
                    hours = minutes // 60
                    minutes = minutes % 60
                    total_minutes += minutes

                    # Insert time in hours and minutes format
                    self.tree.insert("", "end", values=(f"{hours} hrs {minutes} mins",))

                # Update total label (convert total_minutes to hrs:mins)
                total_hours = total_minutes // 60
                total_remaining_minutes = total_minutes % 60
                self.total_label.config(text=f"Total Study Time: {total_hours} hrs {total_remaining_minutes} mins")
        except FileNotFoundError:
            messagebox.showerror("File Not Found",
                                 f"Could not find '{self.csv_path}'.\nMake sure it exists in the same folder.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = StudyTimeApp()
    app.mainloop()
