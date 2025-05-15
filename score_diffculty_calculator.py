import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Paths to input and output files
INPUT_SCORES_FILE = os.path.join('programs', 'study_scores.csv')
OUTPUT_DIFFICULTY_FILE = 'difficulty.csv'

# Configuration: planned tests per subject (optional override)
PLANNED_TESTS = {
    # 'Biology': 6,
    # 'Chemistry': 6,
}
DEFAULT_TOTAL_TESTS = 7


def calculate_difficulty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate difficulty per subject for a single student.
    """
    # Only consider rows where Score is present
    df = df.dropna(subset=['Score'])
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    df = df.dropna(subset=['Score'])

    results = []
    grouped = df.groupby('Subject')
    for subject, group in grouped:
        tests_taken = len(group)
        mean_score = group['Score'].mean()
        planned = PLANNED_TESTS.get(subject, DEFAULT_TOTAL_TESTS)
        factor = planned / tests_taken if tests_taken > 0 else 1
        difficulty = (1 - mean_score / 100.0) * factor
        results.append({
            'Subject': subject,
            'tests_taken': tests_taken,
            'mean_score': round(mean_score, 2),
            'planned_tests': planned,
            'difficulty': round(difficulty, 4)
        })

    return pd.DataFrame(results)


def run_calculation():
    # Check input exists
    if not os.path.exists(INPUT_SCORES_FILE):
        messagebox.showerror('Error', f"Input file '{INPUT_SCORES_FILE}' not found.")
        return

    try:
        df_scores = pd.read_csv(INPUT_SCORES_FILE)
    except Exception as e:
        messagebox.showerror('Error', f"Failed to read CSV:\n{e}")
        return

    required = {'SAC', 'Subject', 'Score'}
    missing = required - set(df_scores.columns)
    if missing:
        messagebox.showerror('Error', f"CSV missing columns: {', '.join(missing)}")
        return

    df_diff = calculate_difficulty(df_scores)
    if df_diff.empty:
        messagebox.showwarning('Warning', 'No valid scores found to calculate difficulty.')
        return

    try:
        df_diff.to_csv(OUTPUT_DIFFICULTY_FILE, index=False)
        messagebox.showinfo('Success', f"Difficulty saved to '{OUTPUT_DIFFICULTY_FILE}'.")
    except Exception as e:
        messagebox.showerror('Error', f"Failed to write CSV:\n{e}")


def main():
    root = tk.Tk()
    root.title('Subject Difficulty Calculator')
    root.geometry('350x170')

    label = tk.Label(root, text='Press to calculate difficulty', font=(None, 12))
    label.pack(pady=10)
    btn = tk.Button(root, text='Calculation', command=run_calculation, font=(None, 12), width=20)
    btn.pack(pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
