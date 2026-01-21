from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin/groups/', views.admin_groups, name='admin_groups'),
    path('admin/groups/create/', views.admin_create_group, name='admin_create_group'),
    path('admin/groups/<int:pk>/edit/', views.admin_edit_group, name='admin_edit_group'),
    path('admin/groups/<int:pk>/students/', views.admin_group_students, name='admin_group_students'),
    path('admin/groups/<int:group_pk>/students/<int:student_pk>/remove/', views.admin_remove_student, name='admin_remove_student'),
    
    # Teacher URLs
    path('teacher/groups/', views.teacher_groups, name='teacher_groups'),
    path('teacher/groups/<int:pk>/attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('teacher/groups/<int:pk>/homeworks/', views.teacher_homeworks, name='teacher_homeworks'),
    path('teacher/groups/<int:pk>/homeworks/create/', views.teacher_create_homework, name='teacher_create_homework'),
    path('teacher/homeworks/<int:pk>/edit/', views.teacher_edit_homework, name='teacher_edit_homework'),
    path('teacher/homeworks/<int:pk>/submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('teacher/submissions/<int:pk>/grade/', views.teacher_grade_submission, name='teacher_grade_submission'),
    
    # Student URLs
    path('student/groups/', views.student_groups, name='student_groups'),
    path('student/groups/<int:pk>/homeworks/', views.student_homeworks, name='student_homeworks'),
    path('student/homeworks/<int:pk>/submit/', views.student_submit_homework, name='student_submit_homework'),
    path('student/support/', views.student_support_requests, name='student_support_requests'),
    
    # Support Teacher URLs
    path('support/requests/', views.support_requests_list, name='support_requests_list'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('hr/', views.HRView.as_view(), name='hr_page'),
]