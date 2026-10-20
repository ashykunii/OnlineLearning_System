import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# --- USER AUTHENTICATION & PROFILES ---

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Student: {self.user.username}"

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='instructor_profile')
    specialty = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Instructor: {self.user.username}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='employee_profile')
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Employee: {self.user.username}"


# --- COURSE INFRASTRUCTURE ---

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# --- CONTENT & ENROLLMENT ---

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="External video streaming link")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True, help_text="PDF or reading material")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    # ========================== YouTube Helpers ==========================

    @property
    def youtube_video_id(self) -> str:
        """Extract YouTube video ID from various URL formats."""
        if not self.video_url:
            return ""

        url = self.video_url.strip()

        # Regex patterns for different YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_\-]{11})',
            r'youtube\.com/.*[?&]v=([a-zA-Z0-9_\-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Fallback: if the URL itself looks like a video ID
        if re.match(r'^[a-zA-Z0-9_\-]{11}$', url):
            return url

        return ""

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_lessons = models.ManyToManyField(Lesson, blank=True, related_name='completed_by')
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} -> {self.course.title}"


# --- ASSIGNMENTS, SUBMISSIONS, & REVIEWS ---

class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    instructor_file = models.FileField(upload_to='assignment_files/', blank=True, null=True, help_text="Optional: Upload answer key, reference materials, or instructions")

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    text_content = models.TextField(blank=True, help_text="Code or answer notes")
    file_attachment = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Grading fields
    score = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student.user.username} on {self.course.title}"