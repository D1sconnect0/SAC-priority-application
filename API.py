import requests
import csv
import os

# Configuration
API_URL = "https://canvas.instructure.com/api/v1"
ACCESS_TOKEN = "7~zP2uKUMuyr4wGRccMFeaRCHNT8K8PhThFu8TGJ9K8m4nFKwZ27zVCQTzMePFQDNC"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_courses():
    url = f"{API_URL}/courses"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def get_total_score(course_id):
    url = f"{API_URL}/courses/{course_id}/enrollments"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    # Assuming the first enrollment is the current user
    enrollment = resp.json()[0]
    return enrollment.get("grades", {}).get("current_score")

def get_assignment_groups(course_id):
    url = f"{API_URL}/courses/{course_id}/assignment_groups?include[]=assignments"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def fetch_and_save_scores(csv_path="programs/study_scores.csv"):
    """
    Fetches course and assignment data from the API and saves to study_scores.csv.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SAC", "Subject", "Score"])
        courses = get_courses()
        for course in courses:
            course_id = course.get("id")
            course_name = course.get("name")
            try:
                total_score = get_total_score(course_id)
                if total_score is not None:
                    writer.writerow(["Total", course_name, total_score])
            except Exception:
                pass
            try:
                groups = get_assignment_groups(course_id)
                for group in groups:
                    if "Assessed Coursework" in group.get("name", ""):
                        for assignment in group.get("assignments", []):
                            name = assignment.get("name")
                            score = assignment.get("score") or assignment.get("points_possible")
                            if score is not None:
                                writer.writerow([group['name'], name, score])
            except Exception:
                pass

def fetch_and_save_exams(csv_path="programs/exams.csv"):
    """
    Fetches upcoming assignments from Canvas and writes them to exams.csv
    Format: name,date,0.5,subject
    """
    import datetime
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Optionally write header: writer.writerow(["name", "date", "difficulty", "subject"])
        courses = get_courses()
        for course in courses:
            course_id = course.get("id")
            course_name = course.get("name")
            try:
                groups = get_assignment_groups(course_id)
                for group in groups:
                    for assignment in group.get("assignments", []):
                        name = assignment.get("name")
                        due_at = assignment.get("due_at")
                        # Only include assignments with a due date in the future
                        if due_at:
                            try:
                                due_date = datetime.datetime.fromisoformat(due_at.replace('Z', '+00:00')).date()
                                if due_date >= datetime.date.today():
                                    writer.writerow([name, due_date.isoformat(), 0.5, course_name])
                            except Exception:
                                continue
            except Exception:
                pass

def main():
    courses = get_courses()
    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name")
        print(f"\nCourse: {course_name} (ID: {course_id})")
        try:
            total_score = get_total_score(course_id)
            print(f"  Total Score: {total_score}")
        except Exception as e:
            print(f"  Total Score: N/A ({e})")
        try:
            groups = get_assignment_groups(course_id)
            for group in groups:
                if "Assessed Coursework" in group.get("name", ""):
                    print(f"  Assignment Group: {group['name']}")
                    for assignment in group.get("assignments", []):
                        name = assignment.get("name")
                        due_at = assignment.get("due_at")
                        points_possible = assignment.get("points_possible")
                        print(f"    Assignment: {name}")
                        print(f"      Due Date: {due_at}")
                        print(f"      Max Mark: {points_possible}")
        except Exception as e:
            print(f"  Assignment Groups: N/A ({e})")

if __name__ == "__main__":
    # For manual testing, fetch and save to CSV
    fetch_and_save_scores()
    fetch_and_save_exams()