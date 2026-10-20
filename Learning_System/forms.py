from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Instructor, Employee

User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['bio']

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['specialty']

from .models import Course, Lesson, Assignment

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'tags', 'price', 'image', 'is_published']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_url', 'video_file', 'document', 'order']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_score', 'instructor_file']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

from .models import Category, Tag, Enrollment, Review

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['is_approved']

class EmployeeStudentForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank if editing and no change is desired.")
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        if self.student:
            self.fields['username'].initial = self.student.user.username
            self.fields['email'].initial = self.student.user.email
            self.fields['bio'].initial = self.student.bio

    def save(self):
        cleaned_data = self.cleaned_data
        if self.student:
            user = self.student.user
            user.username = cleaned_data['username']
            user.email = cleaned_data['email']
            if cleaned_data['password']:
                user.set_password(cleaned_data['password'])
            user.save()
            self.student.bio = cleaned_data['bio']
            self.student.save()
            return self.student
        else:
            user = User.objects.create_user(
                username=cleaned_data['username'],
                email=cleaned_data['email'],
                password=cleaned_data['password'] or 'password123',
                role='student'
            )
            student = Student.objects.create(user=user, bio=cleaned_data['bio'])
            return student

class EmployeeInstructorForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank if editing and no change is desired.")
    specialty = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        if self.instructor:
            self.fields['username'].initial = self.instructor.user.username
            self.fields['email'].initial = self.instructor.user.email
            self.fields['specialty'].initial = self.instructor.specialty

    def save(self):
        cleaned_data = self.cleaned_data
        if self.instructor:
            user = self.instructor.user
            user.username = cleaned_data['username']
            user.email = cleaned_data['email']
            if cleaned_data['password']:
                user.set_password(cleaned_data['password'])
            user.save()
            self.instructor.specialty = cleaned_data['specialty']
            self.instructor.save()
            return self.instructor
        else:
            user = User.objects.create_user(
                username=cleaned_data['username'],
                email=cleaned_data['email'],
                password=cleaned_data['password'] or 'password123',
                role='instructor'
            )
            instructor = Instructor.objects.create(user=user, specialty=cleaned_data['specialty'])
            return instructor

