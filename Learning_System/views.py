from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q
from django.views.generic import ListView, DetailView, RedirectView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Course, Enrollment, Lesson, Assignment, Submission, Review, Category, Tag, Student, Instructor, Employee, User
from .forms import (
    CourseForm, LessonForm, AssignmentForm, CategoryForm, TagForm, 
    EnrollmentForm, ReviewForm, EmployeeStudentForm, EmployeeInstructorForm
)

# --- ROUTING CONTROL ---

class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    """Evaluates user identity token and routes to the target dashboard."""
    def get_redirect_url(self, *args, **kwargs):
        role = self.request.user.role
        if role == 'student':
            return '/dashboard/student/'
        elif role == 'instructor':
            return '/dashboard/instructor/'
        elif role == 'employee':
            return '/dashboard/employee/'
        return '/courses/'


# --- DASHBOARDS CONTROL ---

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'student'

    def get(self, request):
        student, _ = Student.objects.get_or_create(user=request.user)
        enrollments = Enrollment.objects.filter(student=student).prefetch_related('course__lessons', 'completed_lessons')
        
        # Get all instructors student is taking courses from
        instructors = Instructor.objects.filter(courses__enrollments__student=student).distinct()
        
        instructor_id = request.GET.get('instructor')
        if instructor_id:
            enrollments = enrollments.filter(course__instructor_id=instructor_id)
            
        submissions = Submission.objects.filter(student=student).select_related('assignment__lesson__course')
        
        # Calculate localized system tracking variables
        enrolled_courses_data = []
        for enc in enrollments:
            total_lessons = enc.course.lessons.count()
            completed = enc.completed_lessons.count()
            progress = int((completed / total_lessons) * 100) if total_lessons > 0 else 0
            enrolled_courses_data.append({
                'enrollment': enc,
                'progress': progress,
                'is_paid': enc.is_paid
            })

        # Build chart data: graded submissions only
        graded_submissions = submissions.filter(score__isnull=False)
        chart_labels = [s.assignment.title[:20] for s in graded_submissions]
        chart_scores = [s.score for s in graded_submissions]
        chart_max = [s.assignment.max_score for s in graded_submissions]
        import json

        context = {
            'courses_data': enrolled_courses_data,
            'submissions': submissions,
            'instructors': instructors,
            'selected_instructor': int(instructor_id) if instructor_id and instructor_id.isdigit() else None,
            'chart_labels': json.dumps(chart_labels),
            'chart_scores': json.dumps(chart_scores),
            'chart_max': json.dumps(chart_max),
            'has_grades': graded_submissions.exists(),
        }
        return render(request, 'dashboard_student.html', context)


class InstructorDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'instructor'

    def get(self, request):
        instructor, _ = Instructor.objects.get_or_create(user=request.user)
        courses = Course.objects.filter(instructor=instructor).prefetch_related('lessons__assignments')
        students_count = Enrollment.objects.filter(course__instructor=instructor).values('student').distinct().count()
        pending_submissions = Submission.objects.filter(assignment__lesson__course__instructor=instructor, score__isnull=True)

        context = {
            'courses': courses,
            'students_count': students_count,
            'pending_submissions': pending_submissions,
        }
        return render(request, 'dashboard_instructor.html', context)


class EmployeeDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'employee'

    def get(self, request):
        employee, _ = Employee.objects.get_or_create(user=request.user)
        context = {
            'employee': employee,
            'total_students': Student.objects.count(),
            'total_instructors': Instructor.objects.count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.count(),
            'all_courses': Course.objects.all(),
            'all_enrollments': Enrollment.objects.all().select_related('student__user', 'course'),
            'all_reviews': Review.objects.all().select_related('student__user', 'course'),
        }
        return render(request, 'dashboard_employee.html', context)


# --- COURSE ARCHITECTURE & LEARNING INTERFACES ---

class CourseListView(ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        # Apply deterministic filter arrays
        category_id = self.request.GET.get('category')
        tag_id = self.request.GET.get('tag')
        param_instructor_id = self.request.GET.get('instructor')
        q = self.request.GET.get('q')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        if param_instructor_id:
            queryset = queryset.filter(instructor_id=param_instructor_id)
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['instructors'] = Instructor.objects.all()
        context['q'] = self.request.GET.get('q', '')
        
        category_id = self.request.GET.get('category')
        tag_id = self.request.GET.get('tag')
        instructor_id = self.request.GET.get('instructor')
        
        context['selected_category'] = int(category_id) if category_id and category_id.isdigit() else None
        context['selected_tag'] = int(tag_id) if tag_id and tag_id.isdigit() else None
        context['selected_instructor'] = int(instructor_id) if instructor_id and instructor_id.isdigit() else None
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = self.object.lessons.all()
        context['lessons'] = lessons
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        context['is_enrolled'] = False
        context['is_paid'] = False
        context['enrollment_id'] = None

        # Course stats for Coursera-style bar
        lesson_count = lessons.count()
        approved_reviews = self.object.reviews.filter(is_approved=True)
        avg_rating = approved_reviews.aggregate(avg=__import__('django.db.models', fromlist=['Avg']).Avg('rating'))['avg']
        review_count = approved_reviews.count()
        enrolled_count = self.object.enrollments.count()
        context['lesson_count'] = lesson_count
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else None
        context['review_count'] = review_count
        context['enrolled_count'] = enrolled_count

        if self.request.user.is_authenticated and self.request.user.role == 'student':
            student, _ = Student.objects.get_or_create(user=self.request.user)
            enrollment = Enrollment.objects.filter(
                student=student, course=self.object
            ).first()
            if enrollment:
                context['is_enrolled'] = True
                context['is_paid'] = enrollment.is_paid
                context['enrollment_id'] = enrollment.id
        return context


class EnrollCourseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != 'student':
            return redirect('course_list')
        course = get_object_or_404(Course, pk=pk, is_published=True)
        student, _ = Student.objects.get_or_create(user=request.user)
        enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
        
        if course.price == 0:
            enrollment.is_paid = True
            enrollment.save()
            return redirect('student_dashboard')
            
        if enrollment.is_paid:
            return redirect('course_detail', pk=course.id)
            
        return redirect('course_payment', enrollment_id=enrollment.id)


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lesson_detail.html'
    context_object_name = 'lesson'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        course = self.object.course
        if request.user.role == 'student':
            student, _ = Student.objects.get_or_create(user=request.user)
            enrollment = Enrollment.objects.filter(student=student, course=course).first()
            if not enrollment or not enrollment.is_paid:
                return redirect('no_access', course_id=course.id)
        elif request.user.role == 'instructor':
            if course.instructor.user != request.user:
                return redirect('no_access', course_id=course.id)
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object.course
        # Verify access authorization
        assignments = self.object.assignments.all()
        if self.request.user.role == 'student':
            student, _ = Student.objects.get_or_create(user=self.request.user)
            enrollment = Enrollment.objects.filter(student=student, course=course).first()
            context['is_completed'] = enrollment.completed_lessons.filter(id=self.object.id).exists() if enrollment else False
            
            # Attach user submission to each assignment
            for assignment in assignments:
                assignment.user_submission = Submission.objects.filter(
                    assignment=assignment, student=student
                ).first()
        elif self.request.user.role == 'instructor' and course.instructor.user == self.request.user:
            # Attach all student submissions to each assignment
            for assignment in assignments:
                assignment.all_submissions = Submission.objects.filter(assignment=assignment).select_related('student__user')

        context['assignments'] = assignments
        return context


# --- PROGRESSION AND FEEDBACK TRACING ---

class ToggleLessonCompleteView(LoginRequiredMixin, View):
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        student, _ = Student.objects.get_or_create(user=request.user)
        enrollment = get_object_or_404(Enrollment, student=student, course=lesson.course)
        
        if enrollment.completed_lessons.filter(id=lesson.id).exists():
            enrollment.completed_lessons.remove(lesson)
        else:
            enrollment.completed_lessons.add(lesson)
        return redirect('lesson_detail', pk=lesson.id)


class SubmitAssignmentView(LoginRequiredMixin, View):
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        student, _ = Student.objects.get_or_create(user=request.user)
        
        enrollment = Enrollment.objects.filter(student=student, course=assignment.lesson.course).first()
        if not enrollment or not enrollment.is_paid:
            return redirect('no_access', course_id=assignment.lesson.course.id)

        # Instantiate or update an open core tracking model
        submission, created = Submission.objects.get_or_create(assignment=assignment, student=student)
        submission.text_content = request.POST.get('text_content', '')
        if 'file_attachment' in request.FILES:
            submission.file_attachment = request.FILES['file_attachment']
        submission.submitted_at = timezone.now()
        # Reset grading when resubmitting
        submission.score = None
        submission.feedback = ''
        submission.graded_at = None
        submission.save()
        return redirect('lesson_detail', pk=assignment.lesson.id)


class GradeSubmissionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'instructor'

    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        # Verify this instructor owns the course
        if submission.assignment.lesson.course.instructor.user != request.user:
            return redirect('instructor_dashboard')
        submission.score = int(request.POST.get('score'))
        submission.feedback = request.POST.get('feedback', '')
        submission.graded_at = timezone.now()
        submission.save()
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'instructor_dashboard'
        return redirect(next_url)


class AssignmentDetailView(LoginRequiredMixin, View):
    """Dedicated assignment page: students submit here, instructors see all submissions."""

    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        lesson = assignment.lesson
        context = {'assignment': assignment, 'lesson': lesson}

        if request.user.role == 'student':
            student, _ = Student.objects.get_or_create(user=request.user)
            # Verify enrollment and payment
            enrollment = Enrollment.objects.filter(student=student, course=lesson.course).first()
            if not enrollment or not enrollment.is_paid:
                return redirect('no_access', course_id=lesson.course.id)
            context['user_submission'] = Submission.objects.filter(
                assignment=assignment, student=student
            ).first()
        elif request.user.role == 'instructor':
            if lesson.course.instructor.user != request.user:
                return redirect('instructor_dashboard')
            submissions = Submission.objects.filter(assignment=assignment).select_related('student__user')
            context['all_submissions'] = submissions
            context['graded_count'] = submissions.filter(score__isnull=False).count()
            context['pending_count'] = submissions.filter(score__isnull=True).count()

        return render(request, 'assignment_detail.html', context)


class SubmissionListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Instructor-only page listing all submissions for a given assignment."""
    def test_func(self):
        return self.request.user.role == 'instructor'

    def get(self, request, assignment_id):
        instructor, _ = Instructor.objects.get_or_create(user=request.user)
        assignment = get_object_or_404(
            Assignment, pk=assignment_id,
            lesson__course__instructor=instructor
        )
        submissions = Submission.objects.filter(assignment=assignment).select_related('student__user').order_by('-submitted_at')
        context = {
            'assignment': assignment,
            'submissions': submissions,
            'graded_count': submissions.filter(score__isnull=False).count(),
            'pending_count': submissions.filter(score__isnull=True).count(),
        }
        return render(request, 'submission_list.html', context)


class StudentGradesView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Student's complete grades & feedback overview across all assignments."""
    def test_func(self):
        return self.request.user.role == 'student'

    def get(self, request):
        student, _ = Student.objects.get_or_create(user=request.user)
        submissions = (
            Submission.objects.filter(student=student)
            .select_related('assignment__lesson__course')
            .order_by('assignment__lesson__course__title', 'assignment__title')
        )
        # Group by course
        courses_map = {}
        for sub in submissions:
            course = sub.assignment.lesson.course
            if course.id not in courses_map:
                courses_map[course.id] = {'course': course, 'submissions': []}
            courses_map[course.id]['submissions'].append(sub)

        context = {
            'courses_data': list(courses_map.values()),
            'total_graded': submissions.filter(score__isnull=False).count(),
            'total_pending': submissions.filter(score__isnull=True).count(),
        }
        return render(request, 'student_grades.html', context)


class SubmitReviewView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        student, _ = Student.objects.get_or_create(user=request.user)
        # Enforce tracking security
        get_object_or_404(Enrollment, student=student, course=course)
        
        Review.objects.create(
            course=course,
            student=student,
            rating=int(request.POST.get('rating')),
            comment=request.POST.get('comment', '')
        )
        return redirect('course_detail', pk=course.id)

# --- INSTRUCTOR MANAGEMENT VIEWS ---

class InstructorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'instructor'

class CourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'form_template.html'
    
    def form_valid(self, form):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        form.instance.instructor = instructor
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('instructor_dashboard')

class CourseUpdateView(InstructorRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'form_template.html'
    
    def get_queryset(self):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        return Course.objects.filter(instructor=instructor)
        
    def get_success_url(self):
        return reverse_lazy('instructor_dashboard')

class LessonCreateView(InstructorRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'form_template.html'
    
    def form_valid(self, form):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        course = get_object_or_404(Course, pk=self.kwargs['course_id'], instructor=instructor)
        form.instance.course = course
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.kwargs['course_id']})

class LessonUpdateView(InstructorRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'form_template.html'
    
    def get_queryset(self):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        return Lesson.objects.filter(course__instructor=instructor)
        
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.id})

class AssignmentCreateView(InstructorRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'form_template.html'
    
    def form_valid(self, form):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'], course__instructor=instructor)
        form.instance.lesson = lesson
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.kwargs['lesson_id']})

class AssignmentUpdateView(InstructorRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignment_update.html'
    
    def get_queryset(self):
        instructor, _ = Instructor.objects.get_or_create(user=self.request.user)
        return Assignment.objects.filter(lesson__course__instructor=instructor)
        
    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.object.lesson.id})

# --- EMPLOYEE SYSTEM-WIDE DATA GOVERNANCE ---

class EmployeeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'employee'

MODEL_MAPPING = {
    'student': (Student, EmployeeStudentForm),
    'instructor': (Instructor, EmployeeInstructorForm),
    'course': (Course, CourseForm),
    'category': (Category, CategoryForm),
    'tag': (Tag, TagForm),
    'enrollment': (Enrollment, EnrollmentForm),
    'review': (Review, ReviewForm),
}

class EmployeeModelListView(EmployeeRequiredMixin, View):
    def get(self, request, model_name):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        model_class, _ = MODEL_MAPPING[model_name]
        items = model_class.objects.all()
        context = {
            'model_name': model_name,
            'items': items,
            'title': f"Manage {model_name.capitalize()}s",
        }
        return render(request, 'employee_model_list.html', context)

class EmployeeModelCreateView(EmployeeRequiredMixin, View):
    def get(self, request, model_name):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        _, form_class = MODEL_MAPPING[model_name]
        form = form_class()
        return render(request, 'employee_model_form.html', {'form': form, 'model_name': model_name, 'action': 'Create'})

    def post(self, request, model_name):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        _, form_class = MODEL_MAPPING[model_name]
        
        if model_name in ['student', 'instructor']:
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect('employee_model_list', model_name=model_name)
        else:
            form = form_class(request.POST, request.FILES or None)
            if form.is_valid():
                form.save()
                return redirect('employee_model_list', model_name=model_name)
        
        return render(request, 'employee_model_form.html', {'form': form, 'model_name': model_name, 'action': 'Create'})

class EmployeeModelUpdateView(EmployeeRequiredMixin, View):
    def get(self, request, model_name, pk):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        model_class, form_class = MODEL_MAPPING[model_name]
        obj = get_object_or_404(model_class, pk=pk)
        
        if model_name == 'student':
            form = form_class(student=obj)
        elif model_name == 'instructor':
            form = form_class(instructor=obj)
        else:
            form = form_class(instance=obj)
            
        return render(request, 'employee_model_form.html', {'form': form, 'model_name': model_name, 'action': 'Update'})

    def post(self, request, model_name, pk):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        model_class, form_class = MODEL_MAPPING[model_name]
        obj = get_object_or_404(model_class, pk=pk)
        
        if model_name == 'student':
            form = form_class(request.POST, student=obj)
            if form.is_valid():
                form.save()
                return redirect('employee_model_list', model_name=model_name)
        elif model_name == 'instructor':
            form = form_class(request.POST, instructor=obj)
            if form.is_valid():
                form.save()
                return redirect('employee_model_list', model_name=model_name)
        else:
            form = form_class(request.POST, request.FILES or None, instance=obj)
            if form.is_valid():
                form.save()
                return redirect('employee_model_list', model_name=model_name)
                
        return render(request, 'employee_model_form.html', {'form': form, 'model_name': model_name, 'action': 'Update'})

class EmployeeModelDeleteConfirmView(EmployeeRequiredMixin, View):
    def get(self, request, model_name, pk):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        model_class, _ = MODEL_MAPPING[model_name]
        obj = get_object_or_404(model_class, pk=pk)
        return render(request, 'employee_model_delete.html', {
            'object': obj,
            'model_name': model_name,
        })

class EmployeeModelDeleteView(EmployeeRequiredMixin, View):
    def post(self, request, model_name, pk):
        if model_name not in MODEL_MAPPING:
            return redirect('employee_dashboard')
        model_class, _ = MODEL_MAPPING[model_name]
        obj = get_object_or_404(model_class, pk=pk)
        
        if model_name in ['student', 'instructor']:
            user = obj.user
            obj.delete()
            user.delete()
        else:
            obj.delete()
            
        return redirect('employee_model_list', model_name=model_name)


# --- PROFILE, SETTINGS & TASK VIEWS ---

class ProfileView(LoginRequiredMixin, View):
    """Unified profile view — renders role-specific profile data."""
    def get(self, request):
        user = request.user
        profile = None
        role = user.role
        extra = {}

        if role == 'student':
            profile, _ = Student.objects.get_or_create(user=user)
            enrollments = Enrollment.objects.filter(student=profile).select_related('course')
            submissions = Submission.objects.filter(student=profile).select_related('assignment')
            graded = submissions.filter(score__isnull=False).count()
            extra = {
                'enrollments': enrollments,
                'submissions': submissions,
                'graded_count': graded,
                'pending_count': submissions.filter(score__isnull=True).count(),
            }
        elif role == 'instructor':
            profile, _ = Instructor.objects.get_or_create(user=user)
            courses = Course.objects.filter(instructor=profile)
            students_count = Enrollment.objects.filter(course__instructor=profile).values('student').distinct().count()
            extra = {
                'courses': courses,
                'courses_count': courses.count(),
                'students_count': students_count,
            }
        elif role == 'employee':
            profile, _ = Employee.objects.get_or_create(user=user)
            extra = {
                'total_students': Student.objects.count(),
                'total_instructors': Instructor.objects.count(),
                'total_courses': Course.objects.count(),
                'total_enrollments': Enrollment.objects.count(),
            }

        context = {
            'profile': profile,
            'role': role,
            **extra,
        }
        return render(request, 'profile.html', context)

    def post(self, request):
        """Handle inline profile bio/specialty/department update."""
        user = request.user
        role = user.role

        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile-specific fields
        if role == 'student':
            profile, _ = Student.objects.get_or_create(user=user)
            profile.bio = request.POST.get('bio', profile.bio)
            profile.save()
        elif role == 'instructor':
            profile, _ = Instructor.objects.get_or_create(user=user)
            profile.specialty = request.POST.get('specialty', profile.specialty)
            profile.save()
        elif role == 'employee':
            profile, _ = Employee.objects.get_or_create(user=user)
            profile.department = request.POST.get('department', profile.department)
            profile.save()

        return redirect('profile')


class SettingsView(LoginRequiredMixin, View):
    """System settings page — shows account preferences per role."""
    def get(self, request):
        return render(request, 'settings.html', {'user': request.user})


class TasksView(LoginRequiredMixin, View):
    """Unified tasks/assignments page per role."""
    def get(self, request):
        user = request.user
        role = user.role
        context = {'role': role}

        if role == 'student':
            student, _ = Student.objects.get_or_create(user=user)
            # All assignments in enrolled courses
            enrollments = Enrollment.objects.filter(student=student).select_related('course')
            enrolled_courses = [e.course for e in enrollments]
            assignments = Assignment.objects.filter(
                lesson__course__in=enrolled_courses
            ).select_related('lesson__course').order_by('due_date')
            # Which ones student has submitted
            submitted_ids = set(
                Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
            )
            tasks = []
            q = request.GET.get('q', '')
            if q:
                assignments = assignments.filter(Q(title__icontains=q) | Q(description__icontains=q))
            for a in assignments:
                tasks.append({
                    'assignment': a,
                    'submitted': a.id in submitted_ids,
                    'submission': Submission.objects.filter(student=student, assignment=a).first(),
                })
            context.update({'tasks': tasks, 'q': q})

        elif role == 'instructor':
            instructor, _ = Instructor.objects.get_or_create(user=user)
            courses = Course.objects.filter(instructor=instructor)
            q = request.GET.get('q', '')
            assignments = Assignment.objects.filter(
                lesson__course__in=courses
            ).select_related('lesson__course')
            if q:
                assignments = assignments.filter(Q(title__icontains=q) | Q(description__icontains=q))
            context.update({
                'assignments': assignments.order_by('due_date'),
                'q': q,
                'pending_count': Submission.objects.filter(
                    assignment__in=assignments, score__isnull=True
                ).count(),
            })

        elif role == 'employee':
            q = request.GET.get('q', '')
            assignments = Assignment.objects.select_related('lesson__course')
            if q:
                assignments = assignments.filter(Q(title__icontains=q) | Q(description__icontains=q))
            context.update({
                'assignments': assignments.order_by('due_date'),
                'q': q,
                'total_submissions': Submission.objects.count(),
            })

        return render(request, 'tasks.html', context)


# --- PAYMENT AND ACCESS MANAGEMENT ---

class CoursePaymentView(LoginRequiredMixin, View):
    def get(self, request, enrollment_id):
        if request.user.role != 'student':
            return redirect('course_list')
        student, _ = Student.objects.get_or_create(user=request.user)
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
        
        if enrollment.is_paid:
            return redirect('course_detail', pk=enrollment.course.id)
            
        context = {
            'enrollment': enrollment,
            'course': enrollment.course,
        }
        return render(request, 'payment.html', context)
        
    def post(self, request, enrollment_id):
        if request.user.role != 'student':
            return redirect('course_list')
        student, _ = Student.objects.get_or_create(user=request.user)
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
        
        enrollment.is_paid = True
        enrollment.save()
        return redirect('course_detail', pk=enrollment.course.id)


class NoAccessView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = None
        if request.user.role == 'student':
            student, _ = Student.objects.get_or_create(user=request.user)
            enrollment = Enrollment.objects.filter(student=student, course=course).first()
            
        context = {
            'course': course,
            'enrollment': enrollment,
        }
        return render(request, 'no_access.html', context)

