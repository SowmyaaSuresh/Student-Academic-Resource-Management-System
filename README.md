# CampusHub – Student Academic Resource Management System

## 1. Project Description
CampusHub is a web-based Student Academic Resource Management System built with Python Flask and SQLite. It provides a common academic workspace where students can access learning materials and assignments, faculty can share resources and create assignments, and administrators can view registered users.

## 2. Problem Statement
Academic resources and assignment information may be spread across different channels. Students need a simple place to find study materials, view assignment instructions and submit their work. Faculty need a convenient way to share learning resources and publish tasks.

## 3. Objectives
- Organize academic resources in one web application.
- Allow faculty to upload and share study materials.
- Allow faculty to create assignments with due dates.
- Allow students to view resources and submit assignment responses.
- Provide separate student, faculty and administrator views.

## 4. Features / Modules
- Login with role-based access (Student, Faculty and Admin demo accounts).
- Dashboard with resource and assignment summaries.
- Study resource listing and search by title or subject.
- Faculty/Admin resource upload and student download.
- Faculty/Admin assignment creation.
- Student assignment submission and submission status.
- Faculty/Admin submission review.
- Admin user listing.

## 5. Technology Stack
- Frontend: HTML5, CSS3, Jinja templates
- Backend: Python 3 and Flask
- Database: SQLite
- Authentication: Werkzeug password hashing and Flask sessions
- Tools: VS Code, Git and GitHub

## 6. Project Structure
```text
Student_Academic_Resource_Management_System/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── academic_resources.db   # Created automatically on first run
├── uploads/                # Uploaded study files are stored here
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── dashboard.html
    ├── materials.html
    ├── upload_material.html
    ├── assignments.html
    ├── create_assignment.html
    ├── submit_assignment.html
    ├── submissions.html
    ├── users.html
    └── 404.html
```

## 7. Prerequisites
- Python 3.9 or later
- pip package manager
- VS Code or another code editor
- A modern web browser

## 8. Installation
1. Extract the ZIP file.
2. Open the extracted project folder in VS Code.
3. Open the terminal in the project folder.
4. Create and activate a virtual environment (recommended):

   Windows:
   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```

5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 9. Demo Login Accounts
| Role | Email | Password |
|---|---|---|
| Student | student@example.com | student123 |
| Faculty | faculty@example.com | faculty123 |
| Admin | admin@example.com | admin123 |

These are demonstration accounts for local academic evaluation. Change the secret key and demo credentials before any real deployment.

## 10. How to Run
Run the following command:
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser. The database and demo accounts are initialized automatically when the application starts.

## 11. How to Test the Main Features
### Student workflow
1. Sign in using the Student demo account.
2. Open Study Resources and download an available file.
3. Open Assignments and view assignment instructions.
4. Submit an answer or submission note.
5. Confirm that the assignment is marked as Submitted.

### Faculty workflow
1. Log out and sign in using the Faculty demo account.
2. Upload a study resource (PDF or another allowed file type).
3. Create an assignment with a due date.
4. Open Submissions to review student responses.

### Admin workflow
1. Sign in using the Admin demo account.
2. Open Users to view the demo accounts.
3. Check dashboard totals and other available modules.

### Input validation checks
- Try signing in with an incorrect password.
- Try uploading a file type that is not allowed.
- Try submitting forms with required fields left empty.
- Try accessing a faculty-only page as a student.

Record the actual test results and screenshots in the assignment report after running the application.

## 12. Sample Data
A faculty member can upload a file with:
- Title: Unit 1 Notes
- Subject: Data Structures
- Description: Introduction and basic concepts
- File: Any PDF smaller than 10 MB

A faculty member can create an assignment with:
- Title: Array Exercises
- Subject: Data Structures
- Description: Solve the given array problems.
- Due date: Choose a future date.

A student can then view the assignment and submit a written response.

## 13. Known Limitations
- This is an academic prototype intended for local demonstration.
- Assignment submissions are stored as text responses; file attachments for student submissions are not implemented.
- Email notifications and automatic reminders are not included.
- Demo accounts are pre-created; a public self-registration workflow is not included.
- The application does not integrate with a college ERP or external learning management system.

## 14. Future Enhancements
- Add student registration and password reset.
- Add file attachments for assignment submissions.
- Add assignment grading and faculty feedback.
- Add email notifications and due-date reminders.
- Add course-wise enrollment and analytics.

## 15. Team Details
Update this section with the actual student name, register number, project guide and team member contributions, if applicable.

## 16. GitHub Repository
After creating your GitHub repository, paste its URL here.

## 17. Resource Management Module
- Faculty can upload study materials.
- Students can view and download available materials.
- Students can search for resources by title or subject.
