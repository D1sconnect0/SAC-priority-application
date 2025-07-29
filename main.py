import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import csv
import os
import subprocess
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib.util
import threading
import time

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# File paths
CSV_FILE = "programs/exams.csv"
SUBJECTS_FILE = "programs/selected_subjects.csv"
TEST_SCORES_FILE = "programs/study_scores.csv"
DIFFICULTY_FILE = "programs/difficulty.csv"
TARGET_SCORES_FILE = "programs/target_scores.csv"
CACHE_FILE = "programs/cache_timestamp.txt"
CHECK_INTERVAL = 1000
CACHE_DURATION = 300  # 5 minutes in seconds

def should_refresh_cache():
    """Check if cache should be refreshed based on timestamp"""
    if not os.path.exists(CACHE_FILE):
        return True
    
    try:
        with open(CACHE_FILE, 'r') as f:
            last_refresh = float(f.read().strip())
            return (time.time() - last_refresh) > CACHE_DURATION
    except:
        return True

def update_cache_timestamp():
    """Update the cache timestamp"""
    try:
        os.makedirs("programs", exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            f.write(str(time.time()))
    except:
        pass

def update_scores_from_api():
    """
    Calls API.py's fetch_and_save_scores and fetch_and_save_exams to update CSVs before UI loads.
    """
    try:
        api_path = os.path.join(os.path.dirname(__file__), "API.py")
        spec = importlib.util.spec_from_file_location("API", api_path)
        api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api)
        api.fetch_and_save_scores(TEST_SCORES_FILE)
        api.fetch_and_save_exams(CSV_FILE)
        update_cache_timestamp()
    except Exception as e:
        print(f"Warning: Could not update scores/exams from API: {e}")

def load_difficulties():
    difficulties = {}
    if os.path.exists(DIFFICULTY_FILE):
        try:
            with open(DIFFICULTY_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subj = row.get('subject') or row.get('Subject')
                    diff = row.get('difficulty') or row.get('Difficulty')
                    try:
                        difficulty = float(diff)
                        if math.isnan(difficulty):
                            continue
                        difficulties[subj] = difficulty
                    except (TypeError, ValueError):
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error loading difficulties: {e}")
    elif os.path.exists(TEST_SCORES_FILE):
        try:
            with open(TEST_SCORES_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        difficulty = float(row.get('sac_score_percent', 0))
                        if math.isnan(difficulty):
                            continue
                        difficulties[row['subject']] = difficulty
                    except (TypeError, ValueError):
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error loading test scores: {e}")
    return difficulties

def load_target_scores():
    """Load target study scores from CSV file"""
    target_scores = {}
    if os.path.exists(TARGET_SCORES_FILE):
        try:
            with open(TARGET_SCORES_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subject = row.get('Subject', '')
                    target_score = row.get('Target_Score', '')
                    try:
                        score = float(target_score)
                        if not math.isnan(score) and 0 <= score <= 50:
                            target_scores[subject] = score
                    except (TypeError, ValueError):
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error loading target scores: {e}")
    return target_scores

class ExamTodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("📚 Exam Priority Manager")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize theme colors first
        self.update_theme_colors()
        
        # Load all data
        self.load_all_data()
        
        # Create UI components
        self.create_sidebar()
        self.create_main_content()
        
        # Load exams and start periodic check
        self.load_exams_from_csv()
        self.periodic_check()
        
        # Schedule API refresh in background after UI is ready
        self.after(1000, self.check_and_refresh_api)

    def check_and_refresh_api(self):
        """Check if API refresh is needed and do it in background"""
        if should_refresh_cache():
            self.last_update_label.configure(text="Checking for updates...")
            # Run API update in background thread
            def update_in_background():
                try:
                    update_scores_from_api()
                    # Update UI in main thread
                    self.after(0, self.on_api_refresh_complete)
                except Exception as e:
                    print(f"Background API update failed: {e}")
                    self.after(0, lambda: self.last_update_label.configure(text="Update failed"))
            
            thread = threading.Thread(target=update_in_background, daemon=True)
            thread.start()
        else:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.configure(text=f"Last Updated: {current_time} (cached)")

    def on_api_refresh_complete(self):
        """Called when background API refresh completes"""
        # Reload all data
        self.load_all_data()
        
        # Update UI components
        self.create_progress_cards()
        self.load_exams_from_csv()
        
        # Update timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.configure(text=f"Last Updated: {current_time}")

    def load_all_data(self):
        """Load all application data in one method"""
        self.available_subjects = self.load_available_subjects()
        self.test_scores = load_difficulties()
        self.target_scores = load_target_scores()
        self.last_modified_time = self.get_modified_time()
        self.exams = []

    def get_modified_time(self):
        return os.path.getmtime(DIFFICULTY_FILE) if os.path.exists(DIFFICULTY_FILE) else None

    def load_available_subjects(self):
        subjects = []
        
        # Load subjects from selected subjects file
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            subjects.extend(row)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading subjects: {e}")
        
        # Also load subjects from API data (study scores file)
        if os.path.exists(TEST_SCORES_FILE):
            try:
                with open(TEST_SCORES_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        subject = row.get('Subject', '').strip()
                        if subject and subject not in ['SAC', 'Total', 'Assessed Coursework']:
                            # Check if this is a "Total" row (contains actual course names)
                            sac_type = row.get('SAC', '').strip()
                            if sac_type == 'Total':
                                subjects.append(subject)
            except Exception as e:
                print(f"Warning: Error loading subjects from API data: {e}")
        
        return sorted(set(subjects))

    def create_sidebar(self):
        """Create the modern sidebar with controls"""
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="📚 Exam Manager", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Theme toggle
        self.theme_frame = ctk.CTkFrame(self.sidebar_frame)
        self.theme_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.theme_label = ctk.CTkLabel(self.theme_frame, text="Appearance")
        self.theme_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame, 
            text="Dark Mode", 
            command=self.toggle_theme
        )
        self.theme_switch.grid(row=1, column=0, padx=10, pady=5)
        self.theme_switch.select()  # Start in dark mode
        
        # API Status Section
        self.api_frame = ctk.CTkFrame(self.sidebar_frame)
        self.api_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.api_title = ctk.CTkLabel(
            self.api_frame, 
            text="📡 API Status", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.api_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Last update info
        self.last_update_label = ctk.CTkLabel(
            self.api_frame, 
            text="Last Updated: Loading...",
            font=ctk.CTkFont(size=12),
            text_color=("gray70", "gray30")
        )
        self.last_update_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.api_frame,
            text="🔄 Refresh Data",
            command=self.refresh_api_data,
            fg_color=("blue", "blue"),
            width=250
        )
        self.refresh_button.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        # Action buttons
        self.actions_frame = ctk.CTkFrame(self.sidebar_frame)
        self.actions_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.actions_title = ctk.CTkLabel(
            self.actions_frame, 
            text="Quick Actions", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.actions_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Action buttons
        action_buttons = [
            ("🎯 Target Scores", self.open_target_scores_dialog, "orange"),
            ("⏱️ Study Timer", self.open_study_timer, "green"),
            ("📝 Study Log", self.start_studytime, "blue"),
            ("📊 Test Scores", self.open_testscore_app, "blue")
        ]
        
        for i, (text, command, color) in enumerate(action_buttons):
            btn = ctk.CTkButton(
                self.actions_frame,
                text=text,
                command=command,
                fg_color=color,
                width=250
            )
            btn.grid(row=i+1, column=0, padx=20, pady=3, sticky="ew")
        
        # Make the frames expand
        self.api_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(0, weight=1)

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.update_theme_colors()
    
    def update_theme_colors(self):
        """Update matplotlib colors based on current theme"""
        appearance_mode = ctk.get_appearance_mode()
        if appearance_mode == "Dark":
            plt.style.use('dark_background')
            self.bg_color = "#2b2b2b"
            self.text_color = "white"
        else:
            plt.style.use('default')
            self.bg_color = "white"
            self.text_color = "black"
        
        # Update all visualizations if they exist
        if hasattr(self, 'pie_canvas'):
            self.update_all_charts()

    def update_all_charts(self):
        """Update all charts with current data and theme"""
        try:
            self.update_pie_chart()
            self.update_timeline_chart() 
            self.update_progress_chart()
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def create_main_content(self):
        """Create the main content area with tabview"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        self.main_title = ctk.CTkLabel(
            self.main_frame, 
            text="Exam Priority Dashboard", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.main_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame, width=800, height=600)
        self.tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Create tabs
        self.tabview.add("📋 Exam List")
        self.tabview.add("📊 Analytics")
        self.tabview.add("🎯 Progress")
        
        # Setup exam list tab
        self.setup_exam_list_tab()
        
        # Setup analytics tab
        self.setup_analytics_tab()
        
        # Setup progress tab
        self.setup_progress_tab()

    def setup_exam_list_tab(self):
        """Setup the exam list tab with modern scrollable frame"""
        self.exam_list_frame = self.tabview.tab("📋 Exam List")
        self.exam_list_frame.grid_columnconfigure(0, weight=1)
        self.exam_list_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame for exams
        self.exam_scroll_frame = ctk.CTkScrollableFrame(
            self.exam_list_frame, 
            label_text="Upcoming Exams (Sorted by Priority)"
        )
        self.exam_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.exam_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # This will be populated by show_priority method
        self.exam_widgets = []

    def setup_analytics_tab(self):
        """Setup the analytics tab with charts"""
        self.analytics_frame = self.tabview.tab("📊 Analytics")
        self.analytics_frame.grid_columnconfigure(0, weight=1)
        self.analytics_frame.grid_rowconfigure(0, weight=1)
        
        # Create notebook for different charts
        self.chart_frame = ctk.CTkFrame(self.analytics_frame)
        self.chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_rowconfigure(1, weight=1)
        
        # Chart selector
        self.chart_selector = ctk.CTkSegmentedButton(
            self.chart_frame,
            values=["Priority Distribution", "Timeline", "Subject Progress"],
            command=self.on_chart_change
        )
        self.chart_selector.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.chart_selector.set("Priority Distribution")
        
        # Chart area
        self.chart_container = ctk.CTkFrame(self.chart_frame)
        self.chart_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.setup_charts()

    def setup_progress_tab(self):
        """Setup the progress tab with subject progress bars"""
        self.progress_frame = self.tabview.tab("🎯 Progress")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame for progress bars
        self.progress_scroll_frame = ctk.CTkScrollableFrame(
        	self.progress_frame,
        	label_text="Subject Progress & Target Scores"
        )
        self.progress_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.progress_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.create_progress_cards()

    def create_progress_cards(self):
        """Create progress cards for each subject with VCE projections"""
        # Clear existing cards
        if hasattr(self, 'progress_cards'):
            for card in self.progress_cards.values():
                card.destroy()
        
        self.progress_cards = {}
        
        for i, subject in enumerate(self.available_subjects):
            # Create card frame
            card = ctk.CTkFrame(self.progress_scroll_frame)
            card.grid(row=i, column=0, padx=10, pady=8, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            
            # Subject name
            subject_label = ctk.CTkLabel(
                card, 
                text=subject, 
                font=ctk.CTkFont(size=18, weight="bold")
            )
            subject_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
            
            # Current score and target
            current_score = self.get_current_score(subject)
            target_score = self.target_scores.get(subject, 50)  # Default to max study score
            
            # Current score display
            current_label = ctk.CTkLabel(
                card, 
                text=f"📊 Current Study Score: {current_score}/50",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#1f538d", "#3d8bff")
            )
            current_label.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="w")
            
            # Target score display
            target_label = ctk.CTkLabel(
                card, 
                text=f"🎯 Target Study Score: {target_score}/50",
                font=ctk.CTkFont(size=14)
            )
            target_label.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="w")
            
            # VCE Projection
            projection = self.calculate_projected_sac_score(subject, target_score)
            projection_label = ctk.CTkLabel(
                card,
                text=f"📈 VCE Projection: {projection}",
                font=ctk.CTkFont(size=14),
                text_color=("#d63031", "#ff6b6b") if "Need" in projection else ("#00b894", "#00cec9")
            )
            projection_label.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="w")
            
            # Progress bar
            if current_score != "No data" and target_score != "Not set":
                try:
                    current_val = float(current_score)
                    target_val = float(target_score)
                    progress = min(current_val / target_val, 1.0) if target_val > 0 else 0
                    
                    progress_bar = ctk.CTkProgressBar(card, width=300, height=15)
                    progress_bar.set(progress)
                    progress_bar.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="ew")
                    
                    # Progress percentage
                    progress_text = ctk.CTkLabel(
                        card, 
                        text=f"{progress*100:.1f}% of target achieved",
                        font=ctk.CTkFont(size=12),
                        text_color=("gray70", "gray30")
                    )
                    progress_text.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10))
                    
                    # SAC breakdown button
                    sac_btn = ctk.CTkButton(
                        card,
                        text="📋 View SAC Breakdown",
                        width=200,
                        height=30,
                        command=lambda s=subject: self.show_sac_breakdown(s),
                        fg_color=("gray70", "gray30")
                    )
                    sac_btn.grid(row=6, column=0, columnspan=2, padx=20, pady=(5, 20))
                    
                except Exception as e:
                    error_label = ctk.CTkLabel(
                        card,
                        text=f"Error calculating progress: {e}",
                        font=ctk.CTkFont(size=12),
                        text_color="red"
                    )
                    error_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 20))
            
            self.progress_cards[subject] = card

    def get_current_score(self, subject):
        """Get current study score for a subject from API data"""
        if os.path.exists(TEST_SCORES_FILE):
            try:
                with open(TEST_SCORES_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if (row.get('Subject') == subject and 
                            row.get('SAC', '').strip() == 'Total'):
                            score = row.get('Score', '')
                            if score and score != '':
                                return f"{float(score):.1f}"
            except:
                pass
        return "No data"
    
    def calculate_projected_sac_score(self, subject, target_study_score=50):
        """
        Calculate projected SAC score needed based on VCE algorithm
        VCE Study Score = 0.5 * (School-based Assessment) + 0.5 * (External Exam)
        Assumes external exam score will be equal to current SAC performance
        """
        try:
            current_score_str = self.get_current_score(subject)
            if current_score_str == "No data":
                return "No data available"
            
            current_score = float(current_score_str)
            
            # VCE algorithm: Study Score = 0.5 * SAC + 0.5 * Exam
            # Assuming exam performance equals SAC performance for projection
            # target_study_score = 0.5 * required_sac + 0.5 * required_sac
            # target_study_score = required_sac
            
            required_sac_score = target_study_score
            
            # If current score is already at or above target, return current
            if current_score >= required_sac_score:
                return f"Target achieved: {current_score:.1f}/50"
            
            improvement_needed = required_sac_score - current_score
            return f"Need +{improvement_needed:.1f} points (target: {required_sac_score:.1f}/50)"
            
        except Exception as e:
            return f"Calculation error: {e}"
    
    def get_sac_breakdown(self, subject):
        """Get detailed SAC breakdown for a subject"""
        sac_data = []
        if os.path.exists(TEST_SCORES_FILE):
            try:
                with open(TEST_SCORES_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if (row.get('Subject') == subject and 
                            row.get('SAC', '').strip() != 'Total' and
                            row.get('SAC', '').strip() != ''):
                            sac_name = row.get('SAC', '')
                            score = row.get('Score', '')
                            if score and score != '':
                                sac_data.append({
                                    'name': sac_name,
                                    'score': float(score),
                                    'percentage': row.get('Percentage', 'N/A')
                                })
            except Exception as e:
                print(f"Error loading SAC breakdown: {e}")
        return sac_data

    def setup_charts(self):
        """Setup matplotlib charts"""
        # Priority Distribution Chart
        self.pie_fig, self.pie_ax = plt.subplots(figsize=(8, 6))
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, self.chart_container)
        
        # Timeline Chart
        self.timeline_fig, self.timeline_ax = plt.subplots(figsize=(8, 6))
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, self.chart_container)
        
        # Progress Chart
        self.progress_fig, self.progress_ax = plt.subplots(figsize=(8, 6))
        self.progress_canvas = FigureCanvasTkAgg(self.progress_fig, self.chart_container)
        
        # Show initial chart
        self.on_chart_change("Priority Distribution")

    def on_chart_change(self, value):
        """Handle chart selection change"""
        # Hide all canvases first
        for canvas in [self.pie_canvas, self.timeline_canvas, self.progress_canvas]:
            canvas.get_tk_widget().pack_forget()
        
        # Show selected chart
        if value == "Priority Distribution":
            self.pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            self.update_pie_chart()
        elif value == "Timeline":
            self.timeline_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            self.update_timeline_chart()
        elif value == "Subject Progress":
            self.progress_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            self.update_progress_chart()

    def update_pie_chart(self):
        """Update the priority distribution pie chart"""
        self.pie_ax.clear()
        
        if self.exams:
            subject_counts = {}
            for exam in self.exams:
                subj = exam['subject']
                subject_counts[subj] = subject_counts.get(subj, 0) + 1

            priorities = [self.compute_priority(e, subject_counts) for e in self.exams]
            labels = [e['name'] for e in self.exams]
            
            # Modern color palette
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            
            self.pie_ax.pie(
                priorities,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(priorities)],
                textprops={'color': self.text_color, 'fontsize': 10}
            )
            self.pie_ax.set_title("Exam Priority Distribution", 
                                color=self.text_color, fontsize=14, fontweight='bold')
        else:
            self.pie_ax.text(0.5, 0.5, 'No exams to display', 
                           ha='center', va='center', transform=self.pie_ax.transAxes,
                           color=self.text_color, fontsize=12)
        
        self.pie_fig.patch.set_facecolor(self.bg_color)
        self.pie_ax.set_facecolor(self.bg_color)
        self.pie_canvas.draw()

    def update_timeline_chart(self):
        """Update the timeline chart"""
        self.timeline_ax.clear()
        
        if self.exams:
            sorted_exams = sorted(self.exams, key=lambda x: x['datetime'])
            names = [e['name'] for e in sorted_exams]
            
            # Color code by urgency
            colors = []
            for exam in sorted_exams:
                days_left = (exam['datetime'] - datetime.now()).days
                if days_left <= 0:
                    colors.append('#FF6B6B')  # Red - overdue
                elif days_left <= 3:
                    colors.append('#FF8E53')  # Orange - urgent
                elif days_left <= 7:
                    colors.append('#FFEAA7')  # Yellow - soon
                else:
                    colors.append('#74B9FF')  # Blue - later
            
            y_pos = range(len(names))
            bars = self.timeline_ax.barh(y_pos, [1] * len(names), color=colors, alpha=0.8)
            
            self.timeline_ax.set_yticks(y_pos)
            self.timeline_ax.set_yticklabels([n[:20] + '...' if len(n) > 20 else n for n in names], 
                                           color=self.text_color)
            self.timeline_ax.set_xlabel('Timeline', color=self.text_color)
            self.timeline_ax.set_title('Exam Timeline', color=self.text_color, fontsize=14, fontweight='bold')
            
            # Add date labels
            for i, (bar, exam) in enumerate(zip(bars, sorted_exams)):
                date_str = exam['datetime'].strftime('%m/%d')
                self.timeline_ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                                    date_str, ha='left', va='center', color=self.text_color)
        else:
            self.timeline_ax.text(0.5, 0.5, 'No exams to display', 
                                ha='center', va='center', transform=self.timeline_ax.transAxes,
                                color=self.text_color, fontsize=12)
        
        self.timeline_fig.patch.set_facecolor(self.bg_color)
        self.timeline_ax.set_facecolor(self.bg_color)
        self.timeline_ax.tick_params(colors=self.text_color)
        self.timeline_canvas.draw()

    def update_progress_chart(self):
        """Update the subject progress chart"""
        self.progress_ax.clear()
        
        subjects = []
        current_scores = []
        target_scores = []
        
        for subject in self.available_subjects:
            current = self.get_current_score(subject)
            target = self.target_scores.get(subject, None)
            
            if current != "No data" and target is not None:
                subjects.append(subject)
                current_scores.append(float(current))
                target_scores.append(float(target))
        
        if subjects:
            x = range(len(subjects))
            width = 0.35
            
            self.progress_ax.bar([i - width/2 for i in x], current_scores, width, 
                               label='Current Score', color='#74B9FF', alpha=0.8)
            self.progress_ax.bar([i + width/2 for i in x], target_scores, width,
                               label='Target Score', color='#00B894', alpha=0.8)
            
            self.progress_ax.set_xlabel('Subjects', color=self.text_color)
            self.progress_ax.set_ylabel('Score', color=self.text_color)
            self.progress_ax.set_title('Current vs Target Scores', color=self.text_color, 
                                     fontsize=14, fontweight='bold')
            self.progress_ax.set_xticks(x)
            self.progress_ax.set_xticklabels([s[:10] + '...' if len(s) > 10 else s for s in subjects], 
                                           rotation=45, ha='right', color=self.text_color)
            
            legend = self.progress_ax.legend()
            legend.get_frame().set_facecolor(self.bg_color)
            for text in legend.get_texts():
                text.set_color(self.text_color)
            
            self.progress_ax.set_ylim(0, 50)
        else:
            self.progress_ax.text(0.5, 0.5, 'No progress data available', 
                                ha='center', va='center', transform=self.progress_ax.transAxes,
                                color=self.text_color, fontsize=12)
        
        self.progress_fig.patch.set_facecolor(self.bg_color)
        self.progress_ax.set_facecolor(self.bg_color)
        self.progress_ax.tick_params(colors=self.text_color)
        self.progress_canvas.draw()

    def update_visualizations(self):
        """Update all visualizations - deprecated, use update_all_charts"""
        self.update_all_charts()
        self.show_priority()

    def show_priority(self):
        """Display exams in priority order using modern cards"""
        # Clear existing widgets
        for widget in self.exam_widgets:
            widget.destroy()
        self.exam_widgets.clear()
        
        if not self.exams:
            no_exams_label = ctk.CTkLabel(
                self.exam_scroll_frame, 
                text="No exams scheduled. Add an exam to get started!",
                font=ctk.CTkFont(size=16),
                text_color=("gray70", "gray30")
            )
            no_exams_label.grid(row=0, column=0, padx=20, pady=50)
            self.exam_widgets.append(no_exams_label)
            return
        
        # Calculate priorities
        subject_counts = {}
        for exam in self.exams:
            subj = exam['subject']
            subject_counts[subj] = subject_counts.get(subj, 0) + 1
        
        prioritized_with_pr = []
        for exam in self.exams:
            pr = self.compute_priority(exam, subject_counts)
            prioritized_with_pr.append((pr, exam))
        
        prioritized_with_pr.sort(key=lambda x: x[0], reverse=True)
        
        # Create exam cards
        for i, (pr, exam) in enumerate(prioritized_with_pr):
            days_left = (exam['datetime'] - datetime.now()).days
            
            # Determine urgency color
            if days_left <= 0:
                card_color = ("red", "darkred")
                urgency_text = "OVERDUE"
                urgency_color = "white"
            elif days_left <= 3:
                card_color = ("orange", "darkorange")
                urgency_text = "URGENT"
                urgency_color = "white"
            elif days_left <= 7:
                card_color = ("yellow", "gold")
                urgency_text = "SOON"
                urgency_color = "black"
            else:
                card_color = ("lightblue", "blue")
                urgency_text = "LATER"
                urgency_color = "white"
            
            # Create exam card
            exam_card = ctk.CTkFrame(self.exam_scroll_frame, fg_color=card_color)
            exam_card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            exam_card.grid_columnconfigure(1, weight=1)
            
            # Urgency badge
            urgency_label = ctk.CTkLabel(
                exam_card,
                text=urgency_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=urgency_color,
                width=80
            )
            urgency_label.grid(row=0, column=0, rowspan=3, padx=(15, 10), pady=15, sticky="w")
            
            # Exam name
            name_label = ctk.CTkLabel(
                exam_card,
                text=exam['name'],
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=urgency_color
            )
            name_label.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="w")
            
            # Exam details
            date_str = exam['datetime'].strftime("%B %d, %Y")
            target_score = self.target_scores.get(exam['subject'], "Not set")
            target_display = f"{target_score}/50" if target_score != "Not set" else "Not set"
            
            details_text = (f"📅 {date_str} | 🎯 Priority: {pr:.2f} | "
                          f"📚 {exam['subject']} | 🏆 Target: {target_display}")
            
            details_label = ctk.CTkLabel(
                exam_card,
                text=details_text,
                font=ctk.CTkFont(size=14),
                text_color=urgency_color
            )
            details_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
            
            # Days left
            days_text = f"📅 {days_left} days left" if days_left > 0 else "⚠️ OVERDUE"
            days_label = ctk.CTkLabel(
                exam_card,
                text=days_text,
                font=ctk.CTkFont(size=12),
                text_color=urgency_color
            )
            days_label.grid(row=2, column=1, padx=10, pady=(5, 15), sticky="w")
            
            self.exam_widgets.append(exam_card)

    def refresh_api_data(self):
        """Refresh data from API"""
        try:
            self.last_update_label.configure(text="Updating...")
            self.refresh_button.configure(state="disabled")
            
            # Update scores and exams from API
            update_scores_from_api()
            
            # Reload all data
            self.load_all_data()
            
            # Update UI
            if hasattr(self, 'subject_combo'):
                self.subject_combo.configure(values=self.available_subjects)
            
            self.create_progress_cards()
            self.load_exams_from_csv()
            
            # Update timestamp
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.configure(text=f"Last Updated: {current_time}")
            
            messagebox.showinfo("Success", "Data refreshed from API!", parent=self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}", parent=self)
        finally:
            self.refresh_button.configure(state="normal")

    def load_exams_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 4:
                        name, date_str, diff, subject = row
                        try:
                            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
                            difficulty = float(diff)
                            if math.isnan(difficulty):
                                continue
                            self.exams.append({
                                "name": name,
                                "datetime": exam_dt,
                                "difficulty": difficulty,
                                "subject": subject
                            })
                        except ValueError:
                            continue
            self.show_priority()
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading exams: {e}", parent=self)

    def clear_exams(self):
        """Clear all exams - API will repopulate on next refresh"""
        if messagebox.askyesno("Confirm", "Clear all exam data? (Will be repopulated from API on next refresh)", parent=self):
            self.exams.clear()
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                    pass
            self.show_priority()
            self.update_visualizations()

    def calculate_difficulty(self, sac_score_percent, wanted_score=50, sac_marks=100, max_possible_marks=100):
        """
        Calculate difficulty based on VCE performance metrics
        """
        try:
            target_percent = (wanted_score / 50) * 100
            relative_perf = max(0.0, 1 - (sac_score_percent / target_percent))
            mark_weight = sac_marks / max_possible_marks
            return 1 - ((1 - relative_perf) * (1 - mark_weight))
        except:
            return 0.5  # Default difficulty

    def calculate_urgency(self, days_until, k=0.16):
        """
        Calculate urgency based on exponential decay
        """
        try:
            import math
            return math.exp(-k * days_until)
        except:
            return 0.5  # Default urgency

    def calculate_priority_score(self, difficulty, urgency):
        """
        Calculate combined priority score
        """
        try:
            return 1 - ((1 - difficulty) * (1 - urgency))
        except:
            return 0.5  # Default priority

    def compute_priority(self, exam, subject_counts):
        """
        Compute priority score for an exam based on improved algorithm
        """
        try:
            now = datetime.now()
            days_until = (exam['datetime'] - now).days
            
            if days_until <= 0:
                return float('inf')  # Overdue exams get highest priority
            
            # Get current and target study scores
            current_score_str = self.get_current_score(exam['subject'])
            current_score = float(current_score_str) if current_score_str != "No data" else 0
            target_score = self.target_scores.get(exam['subject'], 50)
            
            # Calculate difficulty using new algorithm
            difficulty = self.calculate_difficulty(
                sac_score_percent=current_score * 2,  # Convert to percentage (0-100)
                wanted_score=target_score,
                sac_marks=100,  # Assume standard weighting
                max_possible_marks=100
            )
            
            # Calculate urgency
            urgency = self.calculate_urgency(days_until, k=0.4)
            
            # Calculate combined priority
            priority = self.calculate_priority_score(difficulty, urgency)
            
            # Apply subject count factor
            subject_factor = subject_counts.get(exam['subject'], 1)
            final_priority = priority * (1 + (subject_factor - 1) * 0.1)  # Small boost for multiple exams
            
            return round(max(final_priority, 0.001), 3)  # Minimum priority with rounding
            
        except Exception as e:
            print(f"Error computing priority for {exam.get('name', 'Unknown')}: {e}")
            return 1.0  # Default priority

    def periodic_check(self):
        current_mod = self.get_modified_time()
        if current_mod and current_mod != self.last_modified_time:
            self.test_scores = load_difficulties()
            self.target_scores = load_target_scores()
            self.available_subjects = self.load_available_subjects()
            self.last_modified_time = current_mod
        self.after(CHECK_INTERVAL, self.periodic_check)

    def open_target_scores_dialog(self):
        """Opens a modern dialog window for setting target study scores"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("🎯 Set Target Study Scores")
        dialog.geometry("600x700")
        dialog.transient(self)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Set grab after window is visible
        dialog.after(100, dialog.grab_set)
        
        # Get all subjects from both selected subjects and API data
        all_subjects = set(self.available_subjects)
        
        # Add subjects from API data (study scores file)
        if os.path.exists(TEST_SCORES_FILE):
            try:
                with open(TEST_SCORES_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        subject = row.get('Subject', '').strip()
                        if subject and subject not in ['SAC', 'Total', 'Assessed Coursework']:
                            # Check if this is a "Total" row (contains actual course names)
                            sac_type = row.get('SAC', '').strip()
                            if sac_type == 'Total':
                                all_subjects.add(subject)
            except Exception as e:
                print(f"Error reading API subjects: {e}")
        
        # Convert to sorted list
        all_subjects = sorted(list(all_subjects))
        
        # Main title
        title_label = ctk.CTkLabel(
            dialog, 
            text="🎯 Target Study Scores", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Instructions
        instructions = ctk.CTkLabel(
            dialog, 
            text="Set your target study score for each subject (0-50)\nThese will help prioritize your study schedule",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30")
        )
        instructions.pack(pady=(0, 20))
        
        # Scrollable frame for subjects
        scroll_frame = ctk.CTkScrollableFrame(
            dialog, 
            width=550, 
            height=400,
            label_text="Subject Targets"
        )
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Subject entry fields
        target_vars = {}
        
        for i, subject in enumerate(all_subjects):
            # Subject card
            subject_card = ctk.CTkFrame(scroll_frame)
            subject_card.pack(fill='x', padx=10, pady=5)
            subject_card.grid_columnconfigure(1, weight=1)
            
            # Subject name
            subject_label = ctk.CTkLabel(
                subject_card, 
                text=subject, 
                font=ctk.CTkFont(size=16, weight="bold"),
                width=200,
                anchor="w"
            )
            subject_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            
            # Current target score (if any)
            current_target = self.target_scores.get(subject, "")
            target_var = tk.StringVar(value=str(current_target) if current_target else "")
            target_vars[subject] = target_var
            
            # Entry field
            entry = ctk.CTkEntry(
                subject_card, 
                textvariable=target_var,
                placeholder_text="Target (0-50)",
                width=100
            )
            entry.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="e")
            
            # Current score display (if available from API)
            current_score = self.get_current_score(subject)
            current_label = ctk.CTkLabel(
                subject_card,
                text=f"Current Score: {current_score}",
                font=ctk.CTkFont(size=12),
                text_color=("gray70", "gray30")
            )
            current_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15))
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        def save_target_scores():
            """Save the target scores to CSV file"""
            try:
                # Ensure the programs directory exists
                os.makedirs("programs", exist_ok=True)
                
                # Validate and save scores
                valid_scores = {}
                for subject, var in target_vars.items():
                    score_str = var.get().strip()
                    if score_str:  # Only save non-empty scores
                        try:
                            score = float(score_str)
                            if 0 <= score <= 50:
                                valid_scores[subject] = score
                            else:
                                messagebox.showerror(
                                    "Invalid Score", 
                                    f"Score for {subject} must be between 0 and 50."
                                )
                                return
                        except ValueError:
                            messagebox.showerror(
                                "Invalid Score", 
                                f"Please enter a valid number for {subject}."
                            )
                            return
                
                # Write to CSV
                with open(TARGET_SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Subject', 'Target_Score'])
                    for subject, score in valid_scores.items():
                        writer.writerow([subject, score])
                
                # Update the main app's target scores
                self.target_scores = valid_scores
                
                # Refresh the UI
                self.create_progress_cards()
                self.update_visualizations()
                
                messagebox.showinfo(
                    "Success", 
                    f"Target scores saved for {len(valid_scores)} subjects."
                )
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Failed to save target scores: {e}"
                )
        
        def cancel_dialog():
            dialog.destroy()
        
        # Buttons
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=cancel_dialog,
            fg_color="gray"
        )
        cancel_btn.pack(side='left', padx=(20, 10), pady=15)
        
        save_btn = ctk.CTkButton(
            button_frame, 
            text="💾 Save Target Scores", 
            command=save_target_scores,
            fg_color="green"
        )
        save_btn.pack(side='right', padx=(10, 20), pady=15)
        
        # Focus on the dialog
        dialog.focus_set()

    def show_sac_breakdown(self, subject):
        """Show detailed SAC breakdown for a subject"""
        breakdown_dialog = ctk.CTkToplevel(self)
        breakdown_dialog.title(f"📋 SAC Breakdown - {subject}")
        breakdown_dialog.geometry("600x500")
        breakdown_dialog.transient(self)
        
        # Center the dialog
        breakdown_dialog.update_idletasks()
        x = (breakdown_dialog.winfo_screenwidth() // 2) - (breakdown_dialog.winfo_width() // 2)
        y = (breakdown_dialog.winfo_screenheight() // 2) - (breakdown_dialog.winfo_height() // 2)
        breakdown_dialog.geometry(f"+{x}+{y}")
        
        # Set grab after window is visible
        breakdown_dialog.after(100, breakdown_dialog.grab_set)
        
        # Title
        title_label = ctk.CTkLabel(
            breakdown_dialog,
            text=f"📋 {subject} - SAC Breakdown",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Overall score
        current_score = self.get_current_score(subject)
        target_score = self.target_scores.get(subject, 50)
        
        overall_frame = ctk.CTkFrame(breakdown_dialog)
        overall_frame.pack(pady=10, padx=20, fill="x")
        
        overall_label = ctk.CTkLabel(
            overall_frame,
            text=f"Overall Study Score: {current_score}/50 (Target: {target_score}/50)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        overall_label.pack(pady=15)
        
        # VCE projection
        projection = self.calculate_projected_sac_score(subject, target_score)
        projection_label = ctk.CTkLabel(
            overall_frame,
            text=f"VCE Projection: {projection}",
            font=ctk.CTkFont(size=14),
            text_color=("#d63031", "#ff6b6b") if "Need" in projection else ("#00b894", "#00cec9")
        )
        projection_label.pack(pady=(0, 15))
        
        # SAC details
        sac_frame = ctk.CTkScrollableFrame(
            breakdown_dialog,
            label_text="Individual SAC Scores",
            width=550,
            height=250
        )
        sac_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        sac_data = self.get_sac_breakdown(subject)
        
        if sac_data:
            for i, sac in enumerate(sac_data):
                sac_card = ctk.CTkFrame(sac_frame)
                sac_card.pack(fill='x', padx=10, pady=5)
                sac_card.grid_columnconfigure(1, weight=1)
                
                # SAC name
                sac_name_label = ctk.CTkLabel(
                    sac_card,
                    text=sac['name'],
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w"
                )
                sac_name_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
                
                # Score
                score_label = ctk.CTkLabel(
                    sac_card,
                    text=f"{sac['score']:.1f}/50",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#1f538d", "#3d8bff")
                )
                score_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="e")
                
                # Percentage (if available)
                if sac['percentage'] != 'N/A':
                    percentage_label = ctk.CTkLabel(
                        sac_card,
                        text=f"Weight: {sac['percentage']}",
                        font=ctk.CTkFont(size=12),
                        text_color=("gray70", "gray30")
                    )
                    percentage_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15))
        else:
            no_data_label = ctk.CTkLabel(
                sac_frame,
                text="No detailed SAC data available",
                font=ctk.CTkFont(size=16),
                text_color=("gray70", "gray30")
            )
            no_data_label.pack(pady=50)
        
        # Close button
        close_btn = ctk.CTkButton(
            breakdown_dialog,
            text="Close",
            width=100,
            command=breakdown_dialog.destroy
        )
        close_btn.pack(pady=20)

    def open_study_timer(self):
        """Open a modern study timer dialog"""
        timer_dialog = ctk.CTkToplevel(self)
        timer_dialog.title("⏱️ Study Timer")
        timer_dialog.geometry("500x600")
        timer_dialog.transient(self)
        
        # Center the dialog
        timer_dialog.update_idletasks()
        x = (timer_dialog.winfo_screenwidth() // 2) - (timer_dialog.winfo_width() // 2)
        y = (timer_dialog.winfo_screenheight() // 2) - (timer_dialog.winfo_height() // 2)
        timer_dialog.geometry(f"+{x}+{y}")
        
        # Set grab after window is visible
        timer_dialog.after(100, timer_dialog.grab_set)
        
        # Timer state variables
        self.timer_running = False
        self.timer_paused = False
        self.time_left = 0  # in seconds
        self.timer_job = None
        
        # Main title
        title_label = ctk.CTkLabel(
            timer_dialog, 
            text="⏱️ Study Timer", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(30, 20))
        
        # Timer display frame
        timer_frame = ctk.CTkFrame(timer_dialog, width=400, height=200)
        timer_frame.pack(pady=20, padx=40, fill="x")
        timer_frame.pack_propagate(False)
        
        # Time display
        self.time_display = ctk.CTkLabel(
            timer_frame,
            text="25:00",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=("#1f538d", "#14375e")
        )
        self.time_display.pack(expand=True)
        
        # Progress bar
        self.timer_progress = ctk.CTkProgressBar(timer_dialog, width=400, height=20)
        self.timer_progress.pack(pady=10, padx=40)
        self.timer_progress.set(0)
        
        # Preset time buttons
        preset_frame = ctk.CTkFrame(timer_dialog)
        preset_frame.pack(pady=20, padx=40, fill="x")
        
        preset_label = ctk.CTkLabel(preset_frame, text="Quick Presets:", font=ctk.CTkFont(size=16, weight="bold"))
        preset_label.pack(pady=(15, 10))
        
        preset_buttons_frame = ctk.CTkFrame(preset_frame)
        preset_buttons_frame.pack(pady=(0, 15))
        
        presets = [("Pomodoro", 25), ("Short Break", 5), ("Long Break", 15), ("Deep Focus", 50)]
        for i, (name, minutes) in enumerate(presets):
            btn = ctk.CTkButton(
                preset_buttons_frame,
                text=f"{name}\n{minutes}min",
                width=80,
                height=50,
                command=lambda m=minutes: self.set_timer_minutes(m, timer_dialog)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
        
        # Custom time input
        custom_frame = ctk.CTkFrame(timer_dialog)
        custom_frame.pack(pady=10, padx=40, fill="x")
        
        custom_label = ctk.CTkLabel(custom_frame, text="Custom Time (minutes):", font=ctk.CTkFont(size=14))
        custom_label.pack(pady=(15, 5))
        
        input_frame = ctk.CTkFrame(custom_frame)
        input_frame.pack(pady=(0, 15))
        
        self.custom_time_var = tk.StringVar(value="25")
        custom_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.custom_time_var,
            width=100,
            placeholder_text="Minutes"
        )
        custom_entry.pack(side="left", padx=(10, 5))
        
        set_custom_btn = ctk.CTkButton(
            input_frame,
            text="Set",
            width=60,
            command=lambda: self.set_custom_timer(timer_dialog)
        )
        set_custom_btn.pack(side="left", padx=(5, 10))
        
        # Control buttons
        control_frame = ctk.CTkFrame(timer_dialog)
        control_frame.pack(pady=20, padx=40, fill="x")
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Start",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            command=lambda: self.toggle_timer(timer_dialog),
            width=120,
            height=40
        )
        self.start_btn.pack(side="left", padx=(20, 10), pady=15)
        
        self.reset_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Reset",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="orange",
            command=lambda: self.reset_timer(timer_dialog),
            width=120,
            height=40
        )
        self.reset_btn.pack(side="right", padx=(10, 20), pady=15)
        
        # Set initial timer to 25 minutes
        self.set_timer_minutes(25, timer_dialog)
        
        # Handle dialog close
        def on_close():
            if self.timer_job:
                timer_dialog.after_cancel(self.timer_job)
            timer_dialog.destroy()
        
        timer_dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    def set_timer_minutes(self, minutes, dialog):
        """Set timer to specified minutes"""
        if not self.timer_running:
            self.time_left = minutes * 60
            self.update_timer_display(dialog)
            self.timer_progress.set(0)
    
    def set_custom_timer(self, dialog):
        """Set timer to custom minutes"""
        try:
            minutes = int(self.custom_time_var.get())
            if 1 <= minutes <= 999:
                self.set_timer_minutes(minutes, dialog)
            else:
                messagebox.showwarning("Invalid Time", "Please enter a time between 1 and 999 minutes.")
        except ValueError:
            messagebox.showwarning("Invalid Time", "Please enter a valid number.")
    
    def toggle_timer(self, dialog):
        """Start/pause/resume timer"""
        if not self.timer_running and not self.timer_paused:
            # Start timer
            if self.time_left <= 0:
                self.set_timer_minutes(25, dialog)
            self.timer_running = True
            self.start_btn.configure(text="⏸️ Pause", fg_color="orange")
            self.run_timer(dialog)
        elif self.timer_running:
            # Pause timer
            self.timer_running = False
            self.timer_paused = True
            self.start_btn.configure(text="▶️ Resume", fg_color="green")
            if self.timer_job:
                dialog.after_cancel(self.timer_job)
        elif self.timer_paused:
            # Resume timer
            self.timer_running = True
            self.timer_paused = False
            self.start_btn.configure(text="⏸️ Pause", fg_color="orange")
            self.run_timer(dialog)
    
    def reset_timer(self, dialog):
        """Reset timer to initial state"""
        if self.timer_job:
            dialog.after_cancel(self.timer_job)
        self.timer_running = False
        self.timer_paused = False
        self.set_timer_minutes(25, dialog)
        self.start_btn.configure(text="▶️ Start", fg_color="green")
    
    def run_timer(self, dialog):
        """Run the timer countdown"""
        if self.timer_running and self.time_left > 0:
            self.update_timer_display(dialog)
            self.time_left -= 1
            self.timer_job = dialog.after(1000, lambda: self.run_timer(dialog))
        elif self.time_left <= 0:
            # Timer finished
            self.timer_running = False
            self.timer_paused = False
            self.start_btn.configure(text="▶️ Start", fg_color="green")
            self.time_display.configure(text="00:00", text_color="red")
            self.timer_progress.set(1.0)
            messagebox.showinfo("Timer Complete", "⏰ Time's up! Great job studying!", parent=dialog)
    
    def update_timer_display(self, dialog):
        """Update the timer display"""
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        self.time_display.configure(text=time_text)
        
        # Update progress bar (assuming initial time was set)
        try:
            initial_time = int(self.custom_time_var.get()) * 60
            progress = 1 - (self.time_left / initial_time)
            self.timer_progress.set(max(0, min(1, progress)))
        except:
            pass

    def start_studytime(self):
        try:
            subprocess.Popen(["python", "studytime.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def open_testscore_app(self):
        try:
            subprocess.Popen(["python", "testscore.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def open_subject_difficulty_app(self):
        try:
            subprocess.Popen(["python", "subject_difficulty.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

def is_subjects_file_empty():
    if not os.path.exists(SUBJECTS_FILE):
        return True
    try:
        with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    return False
        return True
    except Exception:
        return True

def update_scores_from_api():
    """
    Calls API.py's fetch_and_save_scores and fetch_and_save_exams to update CSVs before UI loads.
    """
    try:
        api_path = os.path.join(os.path.dirname(__file__), "API.py")
        spec = importlib.util.spec_from_file_location("API", api_path)
        api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api)
        api.fetch_and_save_scores(TEST_SCORES_FILE)
        api.fetch_and_save_exams(CSV_FILE)
    except Exception as e:
        print(f"Warning: Could not update scores/exams from API: {e}")

if __name__ == "__main__":
    # Update CSVs from API before UI loads
    update_scores_from_api()

    if is_subjects_file_empty():
        try:
            subprocess.Popen(["python", "Subject_selection.py"])
            # Show info using tkinter messagebox since app isn't created yet
            import tkinter as tk
            root_temp = tk.Tk()
            root_temp.withdraw()  # Hide the temporary root
            messagebox.showinfo("Info", "Please select subjects first.")
            root_temp.destroy()
        except Exception as e:
            print(f"Error: {e}")

    # Create and run the modern app
    app = ExamTodoApp()
    app.mainloop()