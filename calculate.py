import csv
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

def calculate_subject_averages(file_path, output_path='programs/percentage.csv'):
    subject_totals = {}
    subject_counts = {}

    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subject = row.get('Subject')
                score_str = row.get('Score')

                try:
                    score = float(score_str)
                except (ValueError, TypeError):
                    continue  # Skip invalid or empty scores

                if subject:
                    if subject not in subject_totals:
                        subject_totals[subject] = 0
                        subject_counts[subject] = 0
                    subject_totals[subject] += score
                    subject_counts[subject] += 1

        averages = {
            subject: round(subject_totals[subject] / subject_counts[subject], 2)
            for subject in subject_totals
        }

        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Subject', 'Average Score'])
            for subject, avg in averages.items():
                writer.writerow([subject, avg])

        print("\n[Updated] Averages calculated and saved to 'programs/percentage.csv':")
        for subject, avg in averages.items():
            print(f"{subject}: {avg}")

        return averages

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}

# Define the event handler
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, target_file):
        super().__init__()
        self.target_file = os.path.abspath(target_file)

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.target_file:
            print("\nDetected change in study_scores.csv. Recalculating averages...")
            calculate_subject_averages(self.target_file)

if __name__ == '__main__':
    watch_file = 'programs/study_scores.csv'
    watch_dir = os.path.dirname(os.path.abspath(watch_file))

    # Run once initially
    calculate_subject_averages(watch_file)

    # Set up observer
    event_handler = FileChangeHandler(watch_file)
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()

    print(f"\nWatching for changes in '{watch_file}'...\nPress Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")

    observer.join()
