# Bu kodlarni models.py fayliga qo'shing (oxiriga)
from django.db import models

from erp.models import Group, User

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('group', 'Guruh Chat'),
        ('private', 'Shaxsiy Chat'),
    )
    
    name = models.CharField(max_length=200, blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.room_type == 'group' and self.group:
            return f"Guruh Chat: {self.group.name}"
        return self.name or f"Chat #{self.id}"
    
    def get_other_participant(self, user):
        """Shaxsiy chatda boshqa odamni topish"""
        if self.room_type == 'private':
            return self.participants.exclude(id=user.id).first()
        return None
    
    def get_last_message(self):
        return self.messages.first()

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"

class MessageReadReceipt(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.message.id}"