import requests

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
    main()