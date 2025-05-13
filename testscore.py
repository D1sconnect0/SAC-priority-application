import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

SUBJECTS_FILE = "programs/selected_subjects.csv"
SCORES_FILE = "programs/study_scores.csv"
NUM_SACS = 6

class StudyScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Score Tracker")
        self.subjects = self.load_subjects()
        self.score_vars = {}  # {(sac_index, subject): var}

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

        for i in range(1, NUM_SACS + 1):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"SAC {i}")
            self.build_tab(tab, sac_index=i)

        save_btn = ttk.Button(self.root, text="Save All Scores", command=self.save_scores)
        save_btn.pack(pady=5)

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
            self.score_vars[(sac_index, subj)] = var

    def save_scores(self):
        try:
            with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["SAC", "Subject", "Score"])
                for (sac, subj), var in sorted(self.score_vars.items()):
                    score = var.get().strip()
                    writer.writerow([f"SAC {sac}", subj, score])
            messagebox.showinfo("Success", f"Scores saved to {SCORES_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scores: {e}")

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
                                self.score_vars[(sac_index, subject)].set(score)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load previous scores: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyScoreApp(root)
    root.mainloop()
