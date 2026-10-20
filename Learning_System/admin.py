from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Instructor, Employee, Category, Tag, Course, Lesson, Enrollment, Assignment, Submission, Review

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Role Metadata Settings', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Review)