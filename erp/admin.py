from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Group, GroupStudent, Attendance, Homework, HomeworkSubmission, SupportRequest

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('role', 'phone', 'avatar')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha', {'fields': ('role', 'phone', 'avatar')}),
    )

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at')
    list_filter = ('created_at', 'teacher')
    search_fields = ('name', 'teacher__first_name', 'teacher__last_name')

@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ('group', 'student', 'joined_at')
    list_filter = ('group', 'joined_at')
    search_fields = ('student__first_name', 'student__last_name', 'group__name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'date', 'status', 'created_by')
    list_filter = ('status', 'date', 'group')
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'date'

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'deadline', 'max_score', 'created_by')
    list_filter = ('group', 'deadline')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'score', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at', 'homework__group')
    search_fields = ('student__first_name', 'student__last_name', 'homework__title')
    date_hierarchy = 'submitted_at'

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'scheduled_date', 'scheduled_time', 'status', 'support_teacher')
    list_filter = ('status', 'scheduled_date', 'support_teacher')
    search_fields = ('student__first_name', 'student__last_name', 'topic')
    date_hierarchy = 'scheduled_date'