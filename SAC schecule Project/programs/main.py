import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
import shutil
import subprocess  # 导入 subprocess 模块
import time
from tkcalendar import Calendar  # 导入 Calendar 小部件

CSV_FILE = "exams.csv"
BACKUP_FILE = "exams_backup.csv"
SUBJECTS_FILE = "selected_subjects.csv"  # 保存已选科目的 CSV 文件名
CHECK_INTERVAL = 1000  # 轮询检查文件修改的时间间隔，单位：毫秒

class ExamTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam To-Do List")
        self.exams = []  # list of dicts with keys: name, datetime, difficulty, subject
        self.available_subjects = self.load_available_subjects()
        self.last_modified_time = self.get_subjects_file_modified_time()

        self.create_input_frame()
        self.create_list_frame()
        self.load_exams_from_csv()
        self.periodic_check()

    def get_subjects_file_modified_time(self):
        """获取科目选择文件的最后修改时间。"""
        if os.path.exists(SUBJECTS_FILE):
            return os.path.getmtime(SUBJECTS_FILE)
        return None

    def load_available_subjects(self):
        """从 CSV 文件加载已选择的科目。"""
        subjects = []
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        subjects.extend(row)  # 假设科目保存在一行中
            except Exception as e:
                messagebox.showerror("Error", f"加载科目文件时发生错误：{e}")
        return subjects

    def run_subject_selector(self):
        """运行科目选择器脚本。"""
        try:
            subprocess.Popen(["python", "Subject selection.py"])
        except FileNotFoundError:
            messagebox.showerror("Error", "找不到 Subject selection.py 文件，请确保文件在正确的路径下。")
        except Exception as e:
            messagebox.showerror("Error", f"运行科目选择器时发生错误：{e}")

    def update_available_subjects(self):
        """重新加载并更新可用的科目列表。"""
        new_subjects = self.load_available_subjects()
        if new_subjects != self.available_subjects:
            self.available_subjects = new_subjects
            self.subject_combo['values'] = self.available_subjects
            if self.available_subjects and self.subject_var.get() not in self.available_subjects:
                self.subject_var.set(self.available_subjects[0]) # 设置默认值

    def periodic_check(self):
        """定期检查科目选择文件是否已修改。"""
        current_modified_time = self.get_subjects_file_modified_time()
        if current_modified_time is not None and current_modified_time != self.last_modified_time:
            self.update_available_subjects()
            self.last_modified_time = current_modified_time
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def show_calendar(self):
        """显示日期选择日历。"""
        top = tk.Toplevel(self.root)
        cal = Calendar(top, font="Arial 12", selectmode='day',
                       cursor="hand1")
        cal.grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(top, text="Select Date", command=lambda: self.set_date(cal.get_date(), top)).grid(row=1, column=0, pady=5)

    def set_date(self, selected_date, top_window):
        """将选定的日期设置到日期输入框中。"""
        self.date_var.set(selected_date)
        top_window.destroy()

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Add Exam")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Exam Name:").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="Date:").grid(row=1, column=0, sticky="w")
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var, state="readonly").grid(row=1, column=1, sticky="ew")
        ttk.Button(frame, text="Choose Date", command=self.show_calendar).grid(row=1, column=2, padx=5)

        ttk.Label(frame, text="Difficulty:").grid(row=2, column=0, sticky="w")
        self.diff_var = tk.StringVar(value="Medium")
        self.diff_combo = ttk.Combobox(frame, textvariable=self.diff_var, values=["Low", "Medium", "High"], state="readonly")
        self.diff_combo.grid(row=2, column=1, sticky="ew")

        # 新增科目选择
        ttk.Label(frame, text="Subject:").grid(row=3, column=0, sticky="w")
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(frame, textvariable=self.subject_var, values=self.available_subjects, state="readonly")
        self.subject_combo.grid(row=3, column=1, sticky="ew")
        if self.available_subjects:
            self.subject_var.set(self.available_subjects[0]) # 设置默认值

        add_btn = ttk.Button(frame, text="Add Exam", command=self.add_exam)
        add_btn.grid(row=4, column=0, columnspan=2, pady=5)

        clear_btn = ttk.Button(frame, text="Clear All Exams", command=self.clear_exams)
        clear_btn.grid(row=5, column=0, columnspan=2, pady=5)

        # 添加运行科目选择器的按钮
        subject_selector_btn = ttk.Button(frame, text="打开科目选择", command=self.run_subject_selector)
        subject_selector_btn.grid(row=6, column=0, columnspan=2, pady=5)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0) # 调整列权重

    def create_list_frame(self):
        frame = ttk.LabelFrame(self.root, text="Review Order")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        cols = ("name", "datetime", "difficulty", "subject", "priority")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col.title())
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def add_exam(self):
        name = self.name_var.get().strip()
        date_str = self.date_var.get().strip()
        diff = self.diff_var.get()
        subject = self.subject_var.get()
        if not name or not date_str or not subject:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD")
            return
        exam = {"name": name, "datetime": exam_dt, "difficulty": diff, "subject": subject}
        self.exams.append(exam)
        self.save_exam_to_csv(exam)
        self.name_var.set("")
        self.date_var.set("")
        self.diff_var.set("Medium")
        self.subject_var.set(self.available_subjects[0] if self.available_subjects else "")
        self.show_priority()

    def difficulty_score(self, level):
        return {"Low": 1, "Medium": 2, "High": 3}.get(level, 1)

    def compute_priority(self, exam):
        now = datetime.now()  # Get the current date and time
        delta = (exam["datetime"] - now).total_seconds() / 86400  # Calculate the time difference in days
        if delta <= 0:
            return float('inf')  # If the exam date is in the past, return an infinitely low priority
        return self.difficulty_score(exam["difficulty"]) / delta  # Calculate priority based on difficulty and time remaining

    def show_priority(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        prioritized = sorted(self.exams, key=lambda e: self.compute_priority(e), reverse=True)
        for ex in prioritized:
            pr = self.compute_priority(ex)
            dt_str = ex["datetime"].strftime("%Y-%m-%d")
            self.tree.insert('', 'end', values=(ex["name"], dt_str, ex["difficulty"], ex["subject"], f"{pr:.2f}"))

    def save_exam_to_csv(self, exam):
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([exam["name"], exam["datetime"].strftime("%Y-%m-%d"), exam["difficulty"], exam["subject"]])

    def load_exams_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 4:
                    name, date_str, diff, subject = row
                    try:
                        exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
                        self.exams.append({"name": name, "datetime": exam_dt, "difficulty": diff, "subject": subject})
                    except ValueError:
                        continue
                elif len(row) == 3: # 处理旧的没有 subject 的文件
                    name, date_str, diff = row
                    try:
                        exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
                        self.exams.append({"name": name, "datetime": exam_dt, "difficulty": diff, "subject": ""}) # 默认科目为空
                    except ValueError:
                        continue
        self.show_priority()

    def clear_exams(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all exams?"):
            self.exams.clear()
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                    pass  # overwrite with nothing
            self.show_priority()
            messagebox.showinfo("Info", "Exams cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamTodoApp(root)
    root.mainloop()