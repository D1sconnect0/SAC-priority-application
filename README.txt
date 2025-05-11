Exam Scheduler and Study Tracker
================================

A Python desktop application to help students organize exams and monitor study sessions efficiently.

Table of Contents
-----------------
- Overview
- Setup and Requirements
- Usage
  - Exam Scheduler
  - Clock App
  - Study Time
  - Subject Selection
- File Structure
- CSV Format
- License
- Credits

Overview
--------
Exam Scheduler and Study Tracker is a Python desktop application designed to help students manage exam schedules and track study sessions. 
It provides a graphical interface (built with Python’s standard tkinter library) for entering exam details (subject, date, difficulty) and 
computes a priority for each exam. The app can save exam data to a CSV file, ensuring persistence between sessions. In addition, the suite 
includes tools for real-time clock display and study session timing, both with a GUI interface. These features support better time management 
and planning—important for exam preparation.

Key features:
- Exam Scheduler – Add, view, and sort upcoming exams by subject, date, and difficulty. Exams are saved to a CSV file, and a priority score 
  (based on deadline and difficulty) is calculated automatically.
- Time Zone Clock & Study Timer (clockapp.py) – Displays the current date/time (user-selectable timezone) and lets you start/stop study 
  sessions, recording the duration.
- Study Session Summary (studytime.py) – Shows a log of past study sessions (dates and durations) from the persisted studytime.csv file.
- Subject Selection (Subject_selection.py) – GUI tool to choose up to 6 subjects of interest, which are saved to selected_subjects.csv. 
  The main scheduler uses this file to populate its subject dropdown.

Setup and Requirements
----------------------
This application requires Python 3.8 or newer. It uses only the Python standard library, including tkinter for the GUI and the built-in csv 
module for data storage. No external packages are needed by default. Ensure that Python (with Tk support) is installed on your system. The app 
is cross-platform and should work on Windows, macOS, or Linux.

Usage
-----

### Exam Scheduler

The Exam Scheduler (main_app.py) is the primary interface. To run it, use the command line:

    python main_app.py

In the GUI, select a subject (loaded from selected_subjects.csv), pick the exam date, and set a difficulty level. When you add an exam, it appears 
in the list and is saved to exams.csv. Exams are automatically sorted by priority (soonest and hardest first). You can also edit or remove entries 
as needed.

### Clock App

The Clock App (clockapp.py) shows the current date and time and lets you track study sessions. Launch it with:

    python clockapp.py

In the interface, choose a timezone if needed. Use the Start/Stop buttons to record a study session. Each time you end a session, its start time, 
end time, and duration (in minutes) are appended to studytime.csv for later review.

### Study Time

The Study Time script (studytime.py) reads the studytime.csv file and displays a summary of all recorded study sessions. Run it with:

    python studytime.py

It will list dates and total study time, helping you reflect on your study habits over time.

### Subject Selection

The Subject Selection tool (Subject_selection.py) lets you define which subjects to track. Run it with:

    python "Subject Selection.py"

Pick up to 6 subjects from the provided lists and click Save. The chosen subjects are written to selected_subjects.csv. The Exam Scheduler will 
then use this file to populate its subject dropdown list.

File Structure
--------------
The project files are organized as follows:

- main_app.py – Main exam scheduling GUI application.
- clockapp.py – Date/time display and study session timer app.
- studytime.py – Tool to view a summary of past study sessions.
- Subject_selection.py – GUI for selecting subjects to track.
- selected_subjects.csv – Stores the list of chosen subjects (one per line).
- studytime.csv – Logs each study session's date, start/end time, and duration.
- exams.csv – (Generated) file storing the exams you've added (subject, date, difficulty, priority).
- README.txt – This file.

CSV Format
----------
The application uses CSV files to store data. The formats are:

- selected_subjects.csv: Each line contains one subject name (no header). Example: Mathematics
- exams.csv: Each row has subject,date,difficulty,priority. For example: Biology,2024-05-20,2,1
- studytime.csv: Each row has date,start_time,end_time,duration_minutes. For example: 2024-03-15,14:00,15:30,90

License
-------
This project is distributed under the MIT License.

Credits
-------
Developed by the project author as a student productivity tool. It uses Python’s standard libraries (Tkinter for the GUI and the CSV module for data handling). 
Contributions and improvements are welcome!