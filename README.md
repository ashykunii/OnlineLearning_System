# Online Learning System

A Django-based e-learning management platform where students enroll in courses, instructors publish content and grade assignments, and employees assist with administration.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-MVT-green)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![License](https://img.shields.io/badge/License-Educational%20Use-orange)
![Status](https://img.shields.io/badge/Status-Academic%20Project-yellow)

<!-- Optional: add a banner, logo, or demo GIF here -->
<!-- ![Demo](docs/demo.gif) -->

---

## Table of Contents

- [About the Project](#about-the-project)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Design](#database-design)
- [Demo Accounts](#demo-accounts)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Academic Credits](#academic-credits)
- [License](#license)

---

## About the Project

The platform supports multimedia learning through video lessons, downloadable documents, assignment submissions, grading, course enrollment, and student reviews. Students learn at their own pace, instructors manage their own course content, and employees monitor the system.

The application follows **Role-Based Access Control (RBAC)**, so each user sees only the functionality that fits their role. It demonstrates Django's **Model-View-Template (MVT)** architecture, relational database design with the Django ORM, custom authentication, media management, and many-to-many relationships.

## Objectives

- Develop a complete online learning platform using Django.
- Implement custom authentication with multiple user roles.
- Allow instructors to publish and manage courses.
- Enable students to enroll in courses and monitor their learning progress.
- Support multimedia educational materials.
- Implement assignment submission and grading.
- Allow students to review completed courses.
- Demonstrate proper relational database design using the Django ORM.

## Key Features

- **User Management**: Custom authentication extending `AbstractUser` with Student, Instructor, and Employee roles, each with its own profile and shared login credentials.
- **Course Management**: Instructors create, edit, price, publish, and unpublish courses, upload course images, and organize them with categories and tags.
- **Lesson Management**: Lessons support external video URLs, uploaded videos, PDF documents, reading materials, and ordering. YouTube video IDs are extracted automatically from different URL formats for easy embedding.
- **Enrollment System**: Records the student, course, enrollment date, payment status, and completed lessons. Duplicate enrollments are prevented through database constraints.
- **Assignments & Grading**: Instructors set a title, description, due date, maximum score, and reference materials. Students submit written answers, source code, or files, and instructors score them with personalized feedback.
- **Course Reviews**: Students leave a 1-5 rating and written feedback after completing a course, with an approval status and timestamp.
- **Categories & Tags**: Each course belongs to one category (e.g. Programming, Cybersecurity, Data Science) and can have many tags (e.g. Python, Django, Beginner) for searching and filtering.

## Screenshots

<!-- Store images in a /docs or /screenshots folder -->

| Home Page | Course Detail |
| :-------: | :-----------: |
| ![Home page](docs/home.png) | ![Course detail](docs/course-detail.png) |

| Student Dashboard | Instructor Dashboard |
| :---------------: | :------------------: |
| ![Student dashboard](docs/student-dashboard.png) | ![Instructor dashboard](docs/instructor-dashboard.png) |

## Architecture Overview

The project follows Django's Model-View-Template pattern. Requests are routed to views, which use models (through the ORM) to read and write data, then render templates for the browser.

```
┌──────────────────────────┐
│  Templates (HTML/CSS/JS) │  (Bootstrap UI, lesson pages, dashboards)
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│  Views & URL Routing     │  (Role checks, forms, business logic)
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│  Models (Django ORM)     │  (Users, courses, enrollments, submissions)
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│  SQLite + Media Storage  │  (Database, uploaded images, videos, files)
└──────────────────────────┘
```

| Layer          | Responsibility                                                    |
| -------------- | ----------------------------------------------------------------- |
| **Templates**  | Render pages and the responsive Bootstrap interface               |
| **Views**      | Handle requests, enforce role-based permissions, process forms    |
| **Models**     | Define the relational schema and enforce data constraints         |
| **Media**      | Store uploaded course images, videos, PDFs, and submissions       |

## Tech Stack

| Category   | Technology | Purpose                 |
| ---------- | ---------- | ----------------------- |
| Language   | Python     | Programming language    |
| Backend    | Django     | Backend framework       |
| Frontend   | HTML5      | Page structure          |
| Frontend   | CSS3       | Styling                 |
| Frontend   | Bootstrap  | Responsive UI           |
| Frontend   | JavaScript | Client-side interaction |
| Database   | SQLite     | Data storage            |
| Library    | Pillow     | Image upload handling   |

## Project Structure

<!-- Replace with your actual folders (run `tree /F` on Windows or `tree -I venv` on macOS/Linux) -->

```
OnlineLearning_System/
├── [project_config]/      # Django settings, URLs, WSGI/ASGI
├── [app_name]/            # Models, views, forms, templates
│   ├── models.py          # Database models
│   ├── views.py           # Request handling
│   ├── urls.py            # App routes
│   └── templates/         # HTML templates
├── media/                 # Uploaded images, videos, and files
├── static/                # CSS, JavaScript, images
├── db.sqlite3             # SQLite database
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/ashykunii/OnlineLearning_System.git
   cd OnlineLearning_System
```

2. **Create and activate a virtual environment**
```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```
   If there is no `requirements.txt`, run `pip install django pillow`.

4. **Set up the database**
```bash
   python manage.py makemigrations
   python manage.py migrate
```

5. **Create an administrator account** (optional)
```bash
   python manage.py createsuperuser
```

6. **Run the application**
```bash
   python manage.py runserver
```

7. **Open the app** at `http://127.0.0.1:8000`. The Django admin panel is at `http://127.0.0.1:8000/admin`.

## Configuration

Key Django settings are found in `[project_config]/settings.py`. Adjust these before deploying.

| Setting         | Default (Dev)        | Description                                   |
| --------------- | -------------------- | --------------------------------------------- |
| `SECRET_KEY`    | Generated by Django  | Cryptographic key. Keep it private in production |
| `DEBUG`         | `True`               | Set to `False` in production                  |
| `ALLOWED_HOSTS` | `[]`                 | Domains allowed to serve the app              |
| `MEDIA_ROOT`    | `media/`             | Where uploaded files are stored               |
| `MEDIA_URL`     | `/media/`            | URL prefix for uploaded files                 |
| `DATABASES`     | SQLite (`db.sqlite3`)| Database engine and location                  |

> ⚠️ Never commit a production `SECRET_KEY` or real credentials to version control.

## Usage

1. **Register or log in**: Sign in as a Student, Instructor, or Employee.
2. **Students**: Browse courses, enroll, watch lessons, download resources, submit assignments, and leave reviews after completing a course.
3. **Instructors**: Create courses and lessons, upload learning materials, create assignments, and grade submissions with feedback.
4. **Employees**: Monitor users and courses, and manage system settings through the Django admin panel (if permitted).

## Database Design

| Table          | Primary Key | Foreign Key(s)             | Relationships                                        |
| -------------- | ----------- | -------------------------- | ---------------------------------------------------- |
| **User**       | id          | —                          | One-to-One with Student, Instructor, Employee        |
| **Student**    | user_id     | user_id → User             | One Student → Many Enrollments, Reviews, Submissions |
| **Instructor** | user_id     | user_id → User             | One Instructor → Many Courses                        |
| **Employee**   | user_id     | user_id → User             | One-to-One with User                                 |
| **Category**   | id          | —                          | One Category → Many Courses                          |
| **Tag**        | id          | —                          | Many-to-Many with Courses                            |
| **Course**     | id          | instructor_id, category_id | One Instructor, One Category, Many Lessons           |
| **Lesson**     | id          | course_id                  | One Lesson → Many Assignments                        |
| **Enrollment** | id          | student_id, course_id      | Many Students ↔ Many Courses                         |
| **Assignment** | id          | lesson_id                  | One Assignment → Many Submissions                    |
| **Submission** | id          | assignment_id, student_id  | Many Submissions per Assignment                      |
| **Review**     | id          | student_id, course_id      | Students review Courses                              |

## Demo Accounts

> ⚠️ For local development and testing only. Remove or change these before any public deployment.

| Role                                   | Username      | Password      |
| -------------------------------------- | ------------- | ------------- |
| Student                                | `student1`    | `password123` |
| Instructor                             | `instructor1` | `password123` |
| Employee (Django admin access)         | `employee1`   | `password123` |

## Troubleshooting

<details>
<summary><strong>Port 8000 is already in use</strong></summary>

Another process is using the default port. Run the server on a different port:
```bash
python manage.py runserver 8080
```
</details>

<details>
<summary><strong>Uploaded images or files do not display</strong></summary>

Make sure Pillow is installed (`pip install pillow`), that `MEDIA_ROOT` and `MEDIA_URL` are set in `settings.py`, and that your `urls.py` serves media files during development.
</details>

<details>
<summary><strong>Migration errors after pulling changes</strong></summary>

Apply any new migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
If the errors persist during development, delete `db.sqlite3` and the migration files (except `__init__.py`), then run the commands again. This erases all local data.
</details>

<details>
<summary><strong>Old styles or scripts still showing</strong></summary>

Browsers cache CSS and JavaScript. Do a hard refresh with `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (macOS).
</details>

## Roadmap

- [x] Custom authentication with Student, Instructor, and Employee roles
- [x] Course, lesson, and category/tag management
- [x] Enrollment with duplicate prevention
- [x] Assignment submission and grading
- [x] Course reviews and ratings
- [ ] Online payment integration
- [ ] Course completion certificates
- [ ] Progress analytics dashboard
- [ ] Email notifications
- [ ] Discussion forums per lesson

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

## Academic Credits

* **Project Name:** Online_Learning_System
* **Repository Source:** [GitHub Repository Link](https://github.com/ashykunii/OnlineLearning_System)
* **Author / Developer / Designer:** SOK Sorya
* **Course Assignment:** Final Project Evaluation
* **Course Title:** Web Application Development with Django
* **Supervising Lecturer:** Mr. Ratana
* **License:** This application and its underlying source structure are developed and licensed exclusively for **educational and personal use only**.

## License

This project is developed and licensed exclusively for **educational and personal use only**.

<p align="center">© 2026 SOK Sorya. All Rights Reserved.</p>