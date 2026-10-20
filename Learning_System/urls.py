from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth Architecture
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    
    # Role Dashboards
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/instructor/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('dashboard/employee/', views.EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    # Catalog Discovery & Actions
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/enroll/', views.EnrollCourseView.as_view(), name='enroll_course'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('enrollment/<int:enrollment_id>/payment/', views.CoursePaymentView.as_view(), name='course_payment'),
    path('courses/<int:course_id>/no-access/', views.NoAccessView.as_view(), name='no_access'),
    
    # Practical Grading Engine & Actions
    path('lessons/<int:lesson_id>/toggle-complete/', views.ToggleLessonCompleteView.as_view(), name='toggle_lesson'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:assignment_id>/submit/', views.SubmitAssignmentView.as_view(), name='submit_assignment'),
    path('assignments/<int:assignment_id>/submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<int:pk>/grade/', views.GradeSubmissionView.as_view(), name='grade_submission'),
    path('courses/<int:course_id>/review/', views.SubmitReviewView.as_view(), name='submit_review'),
    path('grades/', views.StudentGradesView.as_view(), name='student_grades'),
    
    # Instructor Management
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:course_id>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:lesson_id>/assignments/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_update'),
    
    # Employee Management System
    path('employee/manage/<str:model_name>/', views.EmployeeModelListView.as_view(), name='employee_model_list'),
    path('employee/manage/<str:model_name>/create/', views.EmployeeModelCreateView.as_view(), name='employee_model_create'),
    path('employee/manage/<str:model_name>/<int:pk>/edit/', views.EmployeeModelUpdateView.as_view(), name='employee_model_edit'),
    path('employee/manage/<str:model_name>/<int:pk>/delete/', views.EmployeeModelDeleteView.as_view(), name='employee_model_delete'),
    path('employee/manage/<str:model_name>/<int:pk>/delete/confirm/', views.EmployeeModelDeleteConfirmView.as_view(), name='employee_model_delete_confirm'),

    # Profile, Settings & Tasks
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('tasks/', views.TasksView.as_view(), name='tasks'),
]