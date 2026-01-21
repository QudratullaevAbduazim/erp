# Bu kodlarni admin.py fayliga qo'shing
from django.contrib import admin
from .models import ChatRoom, Message, MessageReadReceipt

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'group', 'created_at')
    list_filter = ('room_type', 'created_at')
    search_fields = ('name', 'group__name')
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_room', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username')
    
    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = 'Xabar'

@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__username', 'message__content')