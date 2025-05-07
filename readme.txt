# 📚 Exam To-Do List Application

A Python-based desktop GUI application built with **Tkinter** that allows students to manage upcoming exams by tracking their **name**, **date**, **difficulty**, and **subject**. It intelligently prioritizes exams based on urgency and difficulty.

## 🛠 Features

- ✅ Add new exams with name, date, difficulty, and subject
- 📈 Calculates **priority** for each exam: the closer and harder, the higher the priority
- 📂 Saves and loads exam data from CSV files
- 🔁 Automatically updates available subjects from a separate CSV file
- 🧹 Option to clear all exams
- 🧠 Dynamic subject selection by launching a separate `Subject selection.py` file
- 🕒 Monitors subject file changes every second and updates subject list accordingly
- 🎨 Clean and modern UI with `ttk` styling

## 📁 File Structure

## ▶️ How to Run

1. Ensure Python 3 is installed.
2. Install required dependencies (only standard libraries are used).
3. Place `main.py` and the `programs/` folder in the same directory.
4. Run the app:
   ```bash
   python main.py

📌 Usage Notes
Date Format: You must enter the date as YYYY-MM-DD (e.g., 2025-06-12).

Subjects: The subject dropdown is populated from selected_subjects.csv. You can open a selector to change this list using the "Open Subject Selector" button.

Priority Calculation:

Based on difficulty (Low = 1, Medium = 2, High = 3)

Divided by days until the exam

The higher the score, the more urgent and difficult the exam is

📊 Columns Explained
Column	Description
Exam Name	Name/Title of the exam
Date	When the exam is scheduled
Difficulty	Subjective difficulty: Low, Medium, High
Subject	The subject selected from CSV
Priority	Automatically calculated priority value

⚙️ Customization
You can edit selected_subjects.csv manually or via Subject selection.py.

You can add a calendar picker using tkcalendar (commented out code included).

Backup features or additional CSV logging can be added easily.

🐛 Known Limitations
No built-in calendar widget (though placeholder code exists).

No per-exam delete button yet (only full clear).

Assumes local Subject selection.py file exists.

👨‍💻 Author
Zherui Hu

D1SCONNECT0








