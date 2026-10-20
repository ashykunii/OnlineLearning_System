### Django-Based E-Learning Management Platform

## Project Overview

The **Online Learning System** is a web-based educational platform developed using the Django framework. The system provides an integrated learning environment where students can enroll in courses, instructors can create educational content and manage assignments, and employees can assist in administrative operations.

The platform supports multimedia learning through video lessons, downloadable documents, assignment submissions, grading, course enrollment, and student reviews. The application follows Role-Based Access Control (RBAC) to provide different functionalities depending on the user's role.

This project demonstrates the implementation of Django's Model-View-Template (MVT) architecture while utilizing relational database design, user authentication, media management, and many-to-many relationships.

---
## Objectives

The primary objectives of the project are:

* Develop a complete online learning platform using Django.
* Implement custom authentication with multiple user roles.
* Allow instructors to publish and manage courses.
* Enable students to enroll in courses and monitor learning progress.
* Support multimedia educational materials.
* Implement assignment submission and grading.
* Allow students to review completed courses.
* Demonstrate proper relational database design using Django ORM.

---

## Technology Stack

| Technology | Purpose                 |
| ---------- | ----------------------- |
| Python     | Programming Language    |
| Django     | Backend Framework       |
| SQLite     | Database                |
| HTML5      | Page Structure          |
| CSS3       | Styling                 |
| Bootstrap  | Responsive UI           |
| JavaScript | Client-side Interaction |
| Pillow     | Image Upload Handling   |

---


## Features
### User Management

The system includes a custom authentication system extending Django's AbstractUser model.

Supported roles include:

* Student
* Instructor
* Employee

Each role contains its own profile information while sharing the same login credentials.

Features include:

* Registration
* Login
* Logout
* Role-based permissions
* Profile management

---

### Course Management

Instructors can:

* Create courses
* Edit courses
* Upload course images
* Set pricing
* Publish or unpublish courses
* Organize courses into categories
* Assign multiple tags

Students can:

* Browse courses
* View course information
* Enroll in available courses

---

### Lesson Management

Each course contains multiple lessons.

Lessons support:

* External video URLs
* Uploaded video files
* PDF documents
* Reading materials
* Lesson ordering

The system automatically extracts YouTube Video IDs from different URL formats to simplify embedding.

---

### Enrollment System

Students can enroll in available courses.

Each enrollment records:

* Student
* Course
* Enrollment date
* Payment status
* Completed lessons

Duplicate enrollments are prevented through database constraints.

---

### Assignment Management

Instructors can create assignments for each lesson.

Assignments contain:

* Title
* Description
* Due date
* Maximum score
* Optional reference materials

Students can submit:

* Written answers
* Source code
* Uploaded files

---

### Submission & Grading

Each submission stores:

* Assignment
* Student
* Submission text
* Uploaded file
* Submission timestamp
* Score
* Feedback
* Grading date

Instructors can grade submissions and provide personalized feedback.

---

### Course Reviews

Students can submit reviews after completing a course.

Each review includes:

* Rating (1–5)
* Written feedback
* Approval status
* Creation timestamp

---

### Categories & Tags

Courses are organized using:

### Categories

Examples:

* Programming
* Web Development
* Cybersecurity
* Artificial Intelligence
* Data Science

Each course belongs to one category.

### Tags

Courses may have multiple tags such as:

* Python
* Django
* Flutter
* Beginner
* Machine Learning

Tags simplify searching and filtering.

---

## Functional Modules

### Authentication Module

* Registration
* Login
* Logout
* Role Verification

### Student Module

* Browse Courses
* Enroll
* Watch Lessons
* Download Resources
* Submit Assignments
* Leave Reviews

### Instructor Module

* Create Courses
* Upload Learning Materials
* Create Assignments
* Grade Students
* Manage Courses

### Employee Module

* Administrative Management
* User Monitoring
* Course Monitoring

---


## Relational Database Table

| Table          | Primary Key | Foreign Key(s)             | Relationships                                     |
| -------------- | ----------- | -------------------------- | ------------------------------------------------- |
| **User**       | id          | —                          | One-to-One Student, Instructor, Employee          |
| **Student**    | user_id     | user_id → User             | One User → Many Enrollments, Reviews, Submissions |
| **Instructor** | user_id     | user_id → User             | One User → Many Courses                           |
| **Employee**   | user_id     | user_id → User             | One User                                          |
| **Category**   | id          | —                          | One Category → Many Courses                       |
| **Tag**        | id          | —                          | Many-to-Many Courses                              |
| **Course**     | id          | instructor_id, category_id | One Instructor, One Category, Many Lessons        |
| **Lesson**     | id          | course_id                  | One Course → Many Assignments                     |
| **Enrollment** | id          | student_id, course_id      | Many Students ↔ Many Courses                      |
| **Assignment** | id          | lesson_id                  | One Lesson → Many Submissions                     |
| **Submission** | id          | assignment_id, student_id  | Many Submissions per Assignment                   |
| **Review**     | id          | student_id, course_id      | Students review Courses                           |

---


## Authentication Testing

Student;
```
{
    "username": "student1",
    "password": "password123"
}
```
Instructor;
```
{
    "username": "instructor1",
    "password": "password123"
}
```
Employee; with access to admin django and can manage system settings and users
```
{
    "username": "employee1",
    "password": "password123"
}
```
Employee; with no access to admin django
```
{
    "username": "testing",
    "password": "@k1234567*"
}
```

---
## Author of this project

Developed and Designed by SOK Sorya.
Lecturer by Mr.Ratana, Web Development with Django.

## License

This project is for educational and personal use only, and was developed as a practical project.

---

