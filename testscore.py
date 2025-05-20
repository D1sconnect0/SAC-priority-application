import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Use os.path.join for cross-platform file paths
SUBJECTS_FILE = os.path.join("programs", "selected_subjects.csv")
SCORES_FILE = os.path.join("programs", "study_scores.csv")
DEFAULT_TOTAL_TESTS = 7
PLANNED_TESTS = {
    # 'Biology': 6,
}
NUM_SACS = 6
DIFFICULTY_FILE = os.path.join("programs", "difficulty.csv")

class StudyScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Score Tracker")
        self.subjects = self.load_subjects()
        self.score_vars = {}  # {(sac_index, subject): (var, entry)}

        self.create_widgets()
        self.load_existing_scores()

    def load_subjects(self):
        subjects = []
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        subjects.extend(row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load subjects: {e}")
        else:
            messagebox.showwarning("Warning", f"{SUBJECTS_FILE} not found.")
        return sorted(set(subjects))

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.notebook = notebook

        # SAC tabs
        for i in range(1, NUM_SACS + 1):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"SAC {i}")
            self.build_tab(tab, sac_index=i)

        # Summary tab
        self.summary_tab = ttk.Frame(notebook)
        notebook.add(self.summary_tab, text="Summary")

        # Difficulty tab
        self.diff_tab = ttk.Frame(notebook)
        notebook.add(self.diff_tab, text="Difficulty")

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        save_btn = ttk.Button(btn_frame, text="Save All Scores", command=self.save_scores)
        save_btn.grid(row=0, column=0, padx=5)
        summary_btn = ttk.Button(btn_frame, text="Show Summary", command=self.display_summary)
        summary_btn.grid(row=0, column=1, padx=5)

    def build_tab(self, parent, sac_index):
        frame = ttk.LabelFrame(parent, text=f"Enter Scores for SAC {sac_index}")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Subject").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame, text="Score").grid(row=0, column=1, padx=5, pady=5)

        for idx, subj in enumerate(self.subjects, start=1):
            ttk.Label(frame, text=subj).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.grid(row=idx, column=1, padx=5, pady=2)
            self.score_vars[(sac_index, subj)] = (var, entry)

    def save_scores(self):
        try:
            with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["SAC", "Subject", "Score"])
                for (sac, subj), (var, _) in sorted(self.score_vars.items()):
                    score = var.get().strip()
                    if score:
                        if not self.is_valid_score(score):
                            raise ValueError(f"Invalid score '{score}' for {subj} in SAC {sac}. Please enter a number.")
                        writer.writerow([f"SAC {sac}", subj, score])
            messagebox.showinfo("Success", f"Scores saved to {SCORES_FILE}")
            # Automatically calculate difficulty after saving
            self.display_difficulty()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scores: {e}")

    def is_valid_score(self, score):
        try:
            float(score)
            return True
        except ValueError:
            return False

    def load_existing_scores(self):
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sac_str = row.get("SAC", "")
                        if sac_str.startswith("SAC"):
                            sac_index = int(sac_str.split()[1])
                            subject = row.get("Subject", "")
                            score = row.get("Score", "")
                            if (sac_index, subject) in self.score_vars:
                                var, entry = self.score_vars[(sac_index, subject)]
                                var.set(score)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load previous scores: {e}")

    def display_summary(self):
        for widget in self.summary_tab.winfo_children():
            widget.destroy()

        # Gather and highlight
        subject_scores = {subj: {} for subj in self.subjects}
        for (sac, subj), (var, entry) in self.score_vars.items():
            s = var.get().strip()
            if s and self.is_valid_score(s):
                val = float(s)
                subject_scores[subj][sac] = val
                entry.config(background='salmon' if val < 50 else 'white')

        # Table view
        tree = ttk.Treeview(self.summary_tab, columns=("subject","average"), show='headings')
        tree.heading("subject", text="Subject")
        tree.heading("average", text="Avg Score")
        for subj, scores in subject_scores.items():
            avg = round(sum(scores.values())/len(scores), 2) if scores else 0
            tree.insert('', tk.END, values=(subj, avg))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Plot area
        control_frame = ttk.Frame(self.summary_tab)
        control_frame.pack(pady=5)
        ttk.Label(control_frame, text="Select Subject:").grid(row=0, column=0)
        subject_var = tk.StringVar(value=self.subjects[0] if self.subjects else "")
        combo = ttk.Combobox(control_frame, values=self.subjects, textvariable=subject_var, state='readonly')
        combo.grid(row=0, column=1)
        combo.bind('<<ComboboxSelected>>', lambda e: self.plot_subject(subject_var.get(), subject_scores))

        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.summary_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        if self.subjects:
            self.plot_subject(self.subjects[0], subject_scores)

    def display_difficulty(self):
        for w in self.diff_tab.winfo_children():
            w.destroy()
        if not os.path.exists(SCORES_FILE):
            messagebox.showerror("Error", f"Scores file not found: {SCORES_FILE}")
            return
        df = pd.read_csv(SCORES_FILE)
        df = df.dropna(subset=['Score'])
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
        df = df.dropna(subset=['Score'])
        res = []
        for subj, g in df.groupby('Subject'):
            n = g.shape[0]
            m = g['Score'].mean()
            planned = PLANNED_TESTS.get(subj, DEFAULT_TOTAL_TESTS)
            factor = planned / n if n > 0 else 1
            diff = round((1 - m/100) * factor, 4)
            res.append((subj, n, round(m, 2), planned, diff))
        pd.DataFrame(res, columns=['Subject','tests_taken','mean_score','planned_tests','difficulty']) \
          .to_csv(DIFFICULTY_FILE, index=False)
        tree = ttk.Treeview(self.diff_tab, columns=('subject','taken','mean','planned','difficulty'), show='headings')
        for c,h in [('subject','Subject'),('taken','Taken'),('mean','Mean'),('planned','Planned'),('difficulty','Difficulty')]:
            tree.heading(c, text=h)
        for r in res:
            tree.insert('', tk.END, values=r)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        messagebox.showinfo("Done", f"Difficulty saved to {DIFFICULTY_FILE}")

    def plot_subject(self, subj, scores):
        self.ax.clear()
        vals = [scores.get(subj, {}).get(i, 0) for i in range(1, NUM_SACS + 1)]
        self.ax.bar([f"SAC {i}" for i in range(1, NUM_SACS + 1)], vals)
        self.ax.set_title(f"Scores for {subj}")
        self.ax.set_ylim(0, 100)
        if hasattr(self, 'canvas'):
            self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyScoreApp(root)
    root.mainloop()
