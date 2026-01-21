from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg, Count
from .models import User, Group, GroupStudent, Attendance, Homework, HomeworkSubmission, SupportRequest
from .forms import (UserRegistrationForm, GroupForm, GroupStudentForm, AttendanceForm, 
                   HomeworkForm, HomeworkSubmissionForm, GradeSubmissionForm, SupportRequestForm)

# Auth Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        # Input nomlarini aniq ko'rsatamiz
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Login yoki parol noto\'g\'ri!')
            
    return render(request, 'erp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.role == 'admin':
        context['groups_count'] = Group.objects.count()
        context['students_count'] = User.objects.filter(role='student').count()
        context['teachers_count'] = User.objects.filter(role='teacher').count()
        context['recent_groups'] = Group.objects.all()[:5]
        
    elif user.role == 'teacher':
        context['my_groups'] = Group.objects.filter(teacher=user)
        context['pending_submissions'] = HomeworkSubmission.objects.filter(
            homework__group__teacher=user, status='pending'
        ).count()
        
    elif user.role == 'student':
        context['my_groups'] = Group.objects.filter(group_students__student=user)
        context['pending_homeworks'] = Homework.objects.filter(
            group__group_students__student=user
        ).exclude(
            submissions__student=user
        ).filter(deadline__gte=timezone.now()).count()
        
    elif user.role == 'support_teacher':
        context['pending_requests'] = SupportRequest.objects.filter(
            support_teacher=user, status='pending'
        ).count()
    
    return render(request, 'erp/dashboard.html', context)

# Admin Views
@login_required
def admin_groups(request):
    if request.user.role != 'admin':
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('dashboard')
    
    groups = Group.objects.all()
    return render(request, 'erp/admin/groups.html', {'groups': groups})

@login_required
def admin_create_group(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guruh muvaffaqiyatli yaratildi!')
            return redirect('admin_groups')
    else:
        form = GroupForm()
    return render(request, 'erp/admin/group_form.html', {'form': form})

@login_required
def admin_edit_group(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guruh yangilandi!')
            return redirect('admin_groups')
    else:
        form = GroupForm(instance=group)
    return render(request, 'erp/admin/group_form.html', {'form': form, 'group': group})

@login_required
def admin_group_students(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk)
    students = GroupStudent.objects.filter(group=group)
    
    if request.method == 'POST':
        form = GroupStudentForm(request.POST, group=group)
        if form.is_valid():
            gs = form.save(commit=False)
            gs.group = group
            gs.save()
            messages.success(request, 'O\'quvchi guruhga qo\'shildi!')
            return redirect('admin_group_students', pk=pk)
    else:
        form = GroupStudentForm(group=group)
    
    return render(request, 'erp/admin/group_students.html', {
        'group': group, 'students': students, 'form': form
    })

@login_required
def admin_remove_student(request, group_pk, student_pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    gs = get_object_or_404(GroupStudent, group_id=group_pk, student_id=student_pk)
    gs.delete()
    messages.success(request, 'O\'quvchi guruhdan o\'chirildi!')
    return redirect('admin_group_students', pk=group_pk)

# Teacher Views
@login_required
def teacher_groups(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    groups = Group.objects.filter(teacher=request.user)
    return render(request, 'erp/teacher/groups.html', {'groups': groups})

from django.utils.dateparse import parse_date
from django.utils import timezone

@login_required
def teacher_attendance(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk, teacher=request.user)
    students = GroupStudent.objects.filter(group=group)
    today = timezone.now().date()
    
    if request.method == 'POST':
        # Sanani POSTdan olamiz
        raw_date = request.POST.get('date')
        
        # Matn ko'rinishidagi sanani Django date obyektiga o'giramiz
        # Agar sana noto'g'ri formatda kelsa, bugungi sanani oladi
        attendance_date = parse_date(raw_date) if raw_date else today
        
        if not attendance_date:
            attendance_date = today

        for gs in students:
            status = request.POST.get(f'status_{gs.student.id}')
            if status:
                Attendance.objects.update_or_create(
                    group=group, 
                    student=gs.student, 
                    date=attendance_date, # Endi bu xavfsiz formatda
                    defaults={
                        'status': status, 
                        'created_by': request.user
                    }
                )
        messages.success(request, 'Davomat saqlandi!')
        return redirect('teacher_attendance', pk=pk)
    
    # GET so'rovi uchun davomatni olish
    attendances = Attendance.objects.filter(group=group, date=today)
    return render(request, 'erp/teacher/attendance.html', {
        'group': group, 
        'students': students, 
        'today': today, 
        'attendances': attendances
    })

@login_required
def teacher_homeworks(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk, teacher=request.user)
    homeworks = Homework.objects.filter(group=group)
    return render(request, 'erp/teacher/homeworks.html', {'group': group, 'homeworks': homeworks})

@login_required
def teacher_create_homework(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk, teacher=request.user)
    
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.group = group
            homework.created_by = request.user
            homework.save()
            messages.success(request, 'Vazifa yaratildi!')
            return redirect('teacher_homeworks', pk=pk)
    else:
        form = HomeworkForm()
    return render(request, 'erp/teacher/homework_form.html', {'form': form, 'group': group})

@login_required
def teacher_edit_homework(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    homework = get_object_or_404(Homework, pk=pk, group__teacher=request.user)
    
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES, instance=homework)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vazifa yangilandi!')
            return redirect('teacher_homeworks', pk=homework.group.id)
    else:
        form = HomeworkForm(instance=homework)
    return render(request, 'erp/teacher/homework_form.html', {'form': form, 'homework': homework})

@login_required
def teacher_submissions(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    homework = get_object_or_404(Homework, pk=pk, group__teacher=request.user)
    submissions = HomeworkSubmission.objects.filter(homework=homework)
    return render(request, 'erp/teacher/submissions.html', {'homework': homework, 'submissions': submissions})

@login_required
def teacher_grade_submission(request, pk):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    submission = get_object_or_404(HomeworkSubmission, pk=pk, homework__group__teacher=request.user)
    
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            graded = form.save(commit=False)
            graded.graded_at = timezone.now()
            graded.save()
            messages.success(request, 'Baho qo\'yildi!')
            return redirect('teacher_submissions', pk=submission.homework.id)
    else:
        form = GradeSubmissionForm(instance=submission)
    return render(request, 'erp/teacher/grade_form.html', {'form': form, 'submission': submission})

# Student Views
@login_required
def student_groups(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    groups = Group.objects.filter(group_students__student=request.user)
    return render(request, 'erp/student/groups.html', {'groups': groups})

@login_required
def student_homeworks(request, pk):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    group = get_object_or_404(Group, pk=pk, group_students__student=request.user)
    homeworks = Homework.objects.filter(group=group)
    return render(request, 'erp/student/homeworks.html', {'group': group, 'homeworks': homeworks})

@login_required
def student_submit_homework(request, pk):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    homework = get_object_or_404(Homework, pk=pk, group__group_students__student=request.user)
    
    try:
        submission = HomeworkSubmission.objects.get(homework=homework, student=request.user)
    except HomeworkSubmission.DoesNotExist:
        submission = None
    
    if request.method == 'POST':
        form = HomeworkSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.homework = homework
            sub.student = request.user
            sub.save()
            messages.success(request, 'Vazifa topshirildi!')
            return redirect('student_homeworks', pk=homework.group.id)
    else:
        form = HomeworkSubmissionForm(instance=submission)
    return render(request, 'erp/student/submit_form.html', {'form': form, 'homework': homework, 'submission': submission})

@login_required
def student_support_requests(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    requests_list = SupportRequest.objects.filter(student=request.user)
    
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.student = request.user
            req.save()
            messages.success(request, 'So\'rov yuborildi!')
            return redirect('student_support_requests')
    else:
        form = SupportRequestForm()
    
    return render(request, 'erp/student/support_requests.html', {'requests': requests_list, 'form': form})

# Support Teacher Views
@login_required
def support_requests_list(request):
    if request.user.role != 'support_teacher':
        return redirect('dashboard')
    
    requests_list = SupportRequest.objects.filter(support_teacher=request.user)
    
    # Kutilayotganlar sonini hisoblab olamiz
    pending_count = requests_list.filter(status='pending').count()
    
    # Mark as viewed when opened
    for req in requests_list.filter(status='pending'):
        req.status = 'viewed'
        req.viewed_at = timezone.now()
        req.save()
    
    return render(request, 'erp/support/requests.html', {
        'requests': requests_list,
        'pending_count': pending_count # Buni ham yuboramiz
    })
    
    
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import UserUpdateForm
from .models import HomeworkSubmission, SupportRequest

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        
        # Rolga qarab qo'shimcha ma'lumotlar yig'ish
        context = {
            'form': form,
            'user': request.user,
        }

        if request.user.role == 'STUDENT':
            # Talaba uchun: Nechta vazifa topshirgan va nechta rad etilgan
            context['total_submissions'] = HomeworkSubmission.objects.filter(student=request.user).count()
            context['rejected_homeworks'] = HomeworkSubmission.objects.filter(student=request.user, status='rejected').count()

        elif request.user.role == 'TEACHER':
            # O'qituvchi uchun: U biriktirilgan guruhlar soni
            context['my_groups_count'] = request.user.teacher_groups.count() # related_name'ga qarab
            
        elif request.user.role == 'SUPPORT':
            # Support uchun: Unga kelgan jami zaproslar
            context['total_requests'] = SupportRequest.objects.filter(support_teacher=request.user).count()

        return render(request, 'erp/profile.html', context)

    def post(self, request):
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            return redirect('profile')
        
        return render(request, 'erp/profile.html', {'form': form})
    
class HRView(View):
    def get(self, request):
        # HR uchun maxsus dashboard yoki ma'lumotlar
        return render(request, 'erp/hr_page.html')