from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Group, GroupStudent, Attendance, Homework, HomeworkSubmission, SupportRequest

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'teacher', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guruh nomi'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tavsif'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')

class GroupStudentForm(forms.ModelForm):
    class Meta:
        model = GroupStudent
        fields = ('student',)
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role='student')
        if group:
            existing_students = GroupStudent.objects.filter(group=group).values_list('student_id', flat=True)
            self.fields['student'].queryset = self.fields['student'].queryset.exclude(id__in=existing_students)

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('student', 'date', 'status', 'notes')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ('title', 'description', 'file', 'deadline', 'max_score')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vazifa nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tavsif'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'value': 100}),
        }

class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ('file', 'text_answer')
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'text_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Javobingizni kiriting'}),
        }

class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ('score', 'feedback')
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Izoh'}),
        }

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ('support_teacher', 'topic', 'description', 'scheduled_date', 'scheduled_time')
        widgets = {
            'support_teacher': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mavzu'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Batafsil ma\'lumot'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['support_teacher'].queryset = User.objects.filter(role='support_teacher')
        
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar'] # Agar rasm bo'lsa, 'avatar'ni ham qo'shing
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }