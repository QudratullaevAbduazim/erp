from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('support_teacher', 'Support Teacher'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.jpg')
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_groups', limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class GroupStudent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_students')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'student')
        ordering = ['student__first_name']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.group.name}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Keldi'),
        ('absent', 'Kelmadi'),
        ('late', 'Kechikdi'),
        ('excused', 'Sababli'),
    )
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_attendances')
    
    class Meta:
        unique_together = ('group', 'student', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.get_status_display()}"

class Homework(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='homeworks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    deadline = models.DateTimeField()
    max_score = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_homeworks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-deadline']
    
    def __str__(self):
        return f"{self.title} - {self.group.name}"

class HomeworkSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('graded', 'Baholandi'),
        ('rejected', 'Rad etildi'),
    )
    
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text_answer = models.TextField(blank=True, null=True)
    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('homework', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.homework.title}"
    
    def save(self, *args, **kwargs):
        if self.score is not None:
            if self.score < 60:
                self.status = 'rejected'
            else:
                self.status = 'graded'
        super().save(*args, **kwargs)

class SupportRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('viewed', 'Ko\'rildi'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='support_requests')
    support_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'support_teacher'}, related_name='received_requests')
    topic = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.topic} - {self.scheduled_date}"