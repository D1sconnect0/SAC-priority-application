import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class StudyTimeApp(tk.Tk):
    def __init__(self, csv_path="programs/studytime.csv"):
        super().__init__()
        self.title("📚 Study Time Tracker")
        self.geometry("700x500")  # Increase window size for better display
        self.configure(bg="#f0f4f8")
        self.csv_path = csv_path

        # Set style
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
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Study Time Records", font=('Helvetica', 16, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Table frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Table configuration
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("Timestamp", "Duration"), 
            show="headings", 
            height=12
        )
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Duration", text="Duration (H:M:S)")
        self.tree.column("Timestamp", anchor=tk.CENTER, width=220)
        self.tree.column("Duration", anchor=tk.CENTER, width=150)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Separator line
        sep = ttk.Separator(main_frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=15)

        # Total frame
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X)

        self.total_label = ttk.Label(
            total_frame, 
            text="Total Study Time: 0 hrs 0 mins 0 secs", 
            font=('Helvetica', 12, 'bold')
        )
        self.total_label.pack(side=tk.LEFT, padx=5)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Refresh button
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", command=self.load_and_display_data)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Initial data load
        self.load_and_display_data()

    def parse_timedelta(self, td_str):
        """Convert time string (HH:MM:SS.ssssss) to a timedelta object"""
        try:
            # Handle time format with microseconds
            if '.' in td_str:
                time_part, micro_part = td_str.split('.')
                microseconds = int(micro_part)
            else:
                time_part = td_str
                microseconds = 0
            
            parts = list(map(int, time_part.split(':')))
            
            if len(parts) == 3:  # HH:MM:SS
                h, m, s = parts
                return timedelta(hours=h, minutes=m, seconds=s, microseconds=microseconds)
            elif len(parts) == 2:  # MM:SS
                m, s = parts
                return timedelta(minutes=m, seconds=s, microseconds=microseconds)
            else:
                return timedelta(0)
        except (ValueError, AttributeError) as e:
            print(f"Error parsing timedelta '{td_str}': {e}")
            return timedelta(0)

    def format_timedelta(self, td):
        """Format timedelta to HH:MM:SS, ignoring microseconds"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def load_and_display_data(self):
        """Read CSV file and display data"""
        try:
            with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
                # Clear existing data
                for row in self.tree.get_children():
                    self.tree.delete(row)

                total_time = timedelta()
                reader = csv.reader(csvfile)
                
                # Read and display data
                for row_num, row in enumerate(reader):
                    if len(row) < 2:
                        continue
                    
                    timestamp_str, duration_str = row[0], row[1]
                    
                    # Skip possible header row
                    if row_num == 0 and (duration_str.lower() == "duration" or ":" not in duration_str):
                        continue
                    
                    duration = self.parse_timedelta(duration_str)
                    total_time += duration
                    
                    # Format time to HH:MM:SS
                    formatted_time = self.format_timedelta(duration)
                    
                    # Add to table
                    self.tree.insert("", "end", values=(
                        timestamp_str,
                        formatted_time
                    ))

                # Update total time
                total_formatted = self.format_timedelta(total_time)
                h, m, s = map(int, total_formatted.split(':'))
                self.total_label.config(
                    text=f"Total Study Time: {h} hrs {m} mins {s} secs"
                )
                
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found",
                f"Could not find '{self.csv_path}'.\nPlease ensure the file exists."
            )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An error occurred while reading the file:\n{str(e)}"
            )

if __name__ == "__main__":
    app = StudyTimeApp()
    app.mainloop()