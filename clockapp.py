import sys
import csv
import os
from pathlib import Path
from datetime import datetime, timedelta

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Tkinter module is not installed. Please install it before running the application.")
    sys.exit(1)

# Time zone support: require Python 3.9+ or backports
try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError:
    print(
        "ZoneInfo module not available. Please use Python 3.9+ or install backports.zoneinfo and tzdata:\n"
        "    pip install backports.zoneinfo tzdata"
    )
    sys.exit(1)

class TimezoneClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Timezone Clock")
        self.geometry("1000x600")
        self.resizable(True, True)

        # Setup data directory and file
        self.data_dir = Path.home() / "TimezoneClockData"
        self.data_file = self.data_dir / "studytime.csv"
        os.makedirs(self.data_dir, exist_ok=True)

        # Record when the app was opened
        self.start_time = datetime.now()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        time_font = ("Courier New", 120, "bold")
        date_font = ("Helvetica", 36)
        elapsed_font = ("Helvetica", 24, "italic")
        bg_color = "#222222"
        fg_color = "#00FF00"

        main_frame = tk.Frame(self, bg=bg_color)
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.columnconfigure(0, weight=1)

        # Date and time labels
        self.date_label = tk.Label(main_frame, font=date_font, bg=bg_color, fg=fg_color)
        self.date_label.grid(row=0, column=0, pady=(40,10), sticky='n')
        self.time_label = tk.Label(main_frame, font=time_font, bg=bg_color, fg=fg_color)
        self.time_label.grid(row=1, column=0, pady=(0,10), sticky='n')

        # Elapsed study time label
        self.elapsed_label = tk.Label(
            main_frame, 
            font=elapsed_font, 
            bg=bg_color, 
            fg="#FFD700",  # gold for contrast
            text="Study time: 00:00:00"
        )
        self.elapsed_label.grid(row=2, column=0, pady=(0,30), sticky='n')

        # Change timezone button
        self.change_btn = ttk.Button(main_frame, text="Change Timezone", command=self.show_search)
        self.change_btn.grid(row=3, column=0, pady=(0,20))

        # Search frame (hidden initially)
        self.search_frame = ttk.Frame(main_frame)
        self.search_frame.columnconfigure(1, weight=1)
        ttk.Label(self.search_frame, text="Search Timezone:").grid(row=0, column=0, padx=(0,5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=0, column=1, sticky='w')
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_timezones())

        self.all_timezones = sorted(available_timezones())
        self.filtered_timezones = self.all_timezones.copy()
        self.selected_tz = tk.StringVar(value="UTC")
        self.tz_combo = ttk.Combobox(
            self.search_frame,
            textvariable=self.selected_tz,
            values=self.filtered_timezones,
            state="readonly",
            width=30
        )
        self.tz_combo.grid(row=0, column=2, padx=(10,0), sticky='w')
        self.tz_combo.bind("<<ComboboxSelected>>", lambda e: self.update_time())

        # OK button to confirm timezone
        self.ok_btn = ttk.Button(self.search_frame, text="OK", command=self.confirm_timezone)
        self.ok_btn.grid(row=0, column=3, padx=(10,0))

        # Hide search frame initially
        self.search_frame.grid(row=4, column=0, pady=10, padx=20, sticky='ew')
        self.search_frame.grid_remove()

        # Start the update loop
        self._running = True
        self._update_loop()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show_search(self):
        self.search_frame.grid()
        self.change_btn.config(state='disabled')
        self.search_entry.focus()

    def confirm_timezone(self):
        self.search_frame.grid_remove()
        self.change_btn.config(state='normal')
        self.update_time()

    def filter_timezones(self):
        q = self.search_var.get().lower()
        self.filtered_timezones = [tz for tz in self.all_timezones if q in tz.lower()] if q else self.all_timezones.copy()
        self.tz_combo['values'] = self.filtered_timezones
        if self.selected_tz.get() not in self.filtered_timezones:
            self.selected_tz.set('')

    def _update_loop(self):
        if not self._running:
            return
        self.update_time()
        self.after(1000, self._update_loop)

    def update_time(self):
        # Update the clock
        tz_name = self.selected_tz.get()
        if tz_name:
            try:
                tz = ZoneInfo(tz_name)
                now = datetime.now(tz)
                self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
                self.time_label.config(text=now.strftime("%H:%M:%S"))
            except Exception:
                self.date_label.config(text="Invalid timezone")
                self.time_label.config(text="--:--:--")
        else:
            self.date_label.config(text="Select a timezone")
            self.time_label.config(text="--:--:--")

        # Update elapsed study time
        elapsed: timedelta = datetime.now() - self.start_time
        hours, rem = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        self.elapsed_label.config(text=f"Study time: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def _on_close(self):
        # Record the study time in the CSV file when the app is closed
        elapsed_time = datetime.now() - self.start_time
        
        try:
            # Check if file exists to write header
            file_exists = os.path.isfile(self.data_file)
            
            with open(self.data_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Duration'])  # Write header if new file
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    str(elapsed_time)
                ])
                
        except PermissionError:
            messagebox.showerror(
                "Permission Denied", 
                f"Cannot write to {self.data_file}. Please check your permissions."
            )
        except OSError as e:
            messagebox.showerror(
                "File System Error", 
                f"Could not save study time: {e.strerror}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An unexpected error occurred: {str(e)}"
            )

        self._running = False
        self.destroy()

if __name__ == "__main__":
    try:
        app = TimezoneClockApp()
        app.mainloop()
    except Exception as e:
        print("Error starting application:", e)
        sys.exit(1)