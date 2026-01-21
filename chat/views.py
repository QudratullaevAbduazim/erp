# Bu kodlarni views.py fayliga qo'shing (oxiriga)

from django.http import JsonResponse
from django.db.models import Q, Count, Max
from .models import ChatRoom, Message, MessageReadReceipt
from erp.models import User, GroupStudent, Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


# Chat Views
@login_required
def chat_list(request):
    """Barcha chatlarni shablon talab qilgan formatda ko'rsatish"""
    user = request.user
    
    # Foydalanuvchi ishtirokchi bo'lgan xonalarni olish
    rooms = ChatRoom.objects.filter(participants=user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    chat_data = []
    for room in rooms:
        # Shaxsiy chat bo'lsa, ikkinchi foydalanuvchini topish
        other_participant = None
        if room.room_type == 'private':
            other_participant = room.participants.exclude(id=user.id).first()
        
        # Unread count (o'qilmagan xabarlar)
        unread_count = Message.objects.filter(
            chat_room=room, 
            is_read=False
        ).exclude(sender=user).count()
        
        # Xonaga unread_count ni vaqtincha biriktirib qo'yamiz
        room.unread_count = unread_count
        
        chat_data.append({
            'room': room,
            'other_participant': other_participant
        })
    
    return render(request, 'erp/chat/chat_list.html', {
        'chat_data': chat_data
    })
@login_required
def chat_room(request, room_id):
    """Chat xonasi"""
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Xabarlarni o'qilgan deb belgilash
    unread_messages = Message.objects.filter(
        chat_room=chat_room
    ).exclude(sender=request.user).exclude(
        read_receipts__user=request.user
    )
    
    for message in unread_messages:
        MessageReadReceipt.objects.get_or_create(
            message=message,
            user=request.user
        )
    
    # Xabarlar
    messages = Message.objects.filter(chat_room=chat_room).select_related('sender').order_by('created_at')
    
    # Boshqa ishtirokchi (shaxsiy chat uchun)
    other_participant = chat_room.get_other_participant(request.user) if chat_room.room_type == 'private' else None
    
    return render(request, 'erp/chat/chat_room.html', {
        'chat_room': chat_room,
        'messages': messages,
        'other_participant': other_participant
    })

@login_required
def send_message(request, room_id):
    """Xabar yuborish (AJAX)"""
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        content = request.POST.get('content', '').strip()
        file = request.FILES.get('file')
        
        if content or file:
            message = Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content,
                file=file
            )
            
            # Chat room yangilash vaqtini o'zgartirish
            chat_room.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender_name': message.sender.get_full_name(),
                    'sender_id': message.sender.id,
                    'created_at': message.created_at.strftime('%H:%M'),
                    'file_url': message.file.url if message.file else None
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Xabar bo\'sh'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def get_messages(request, room_id):
    """Yangi xabarlarni olish (AJAX polling)"""
    chat_room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    last_message_id = request.GET.get('last_message_id', 0)
    
    messages = Message.objects.filter(
        chat_room=chat_room,
        id__gt=last_message_id
    ).select_related('sender').order_by('created_at')
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender_name': msg.sender.get_full_name(),
        'sender_id': msg.sender.id,
        'created_at': msg.created_at.strftime('%H:%M'),
        'file_url': msg.file.url if msg.file else None
    } for msg in messages]
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })

@login_required
def create_private_chat(request, user_id):
    """Shaxsiy chat yaratish yoki mavjud chatga o'tish"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Mavjud chatni tekshirish
    existing_chat = ChatRoom.objects.filter(
        room_type='private',
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_chat:
        return redirect('chat_room', room_id=existing_chat.id)
    
    # Yangi chat yaratish
    chat_room = ChatRoom.objects.create(
        name=f"{request.user.get_full_name()} - {other_user.get_full_name()}",
        room_type='private'
    )
    chat_room.participants.add(request.user, other_user)
    
    messages.success(request, f"{other_user.get_full_name()} bilan chat yaratildi!")
    return redirect('chat_room', room_id=chat_room.id)

@login_required
def group_chat(request, group_id):
    """Guruh chati"""
    group = get_object_or_404(Group, id=group_id)
    
    # Foydalanuvchi guruhga a'zo ekanligini tekshirish
    is_member = False
    if request.user.role == 'teacher' and group.teacher == request.user:
        is_member = True
    elif request.user.role == 'student' and GroupStudent.objects.filter(group=group, student=request.user).exists():
        is_member = True
    elif request.user.role == 'admin':
        is_member = True
    
    if not is_member:
        messages.error(request, "Siz bu guruhga a'zo emassiz!")
        return redirect('dashboard')
    
    # Guruh chatini topish yoki yaratish
    chat_room, created = ChatRoom.objects.get_or_create(
        group=group,
        room_type='group',
        defaults={'name': f"{group.name} Chat"}
    )
    
    # Ishtirokchilarni qo'shish
    if created or chat_room.participants.count() == 0:
        # O'qituvchini qo'shish
        if group.teacher:
            chat_room.participants.add(group.teacher)
        
        # O'quvchilarni qo'shish
        students = User.objects.filter(groupstudent__group=group)
        chat_room.participants.add(*students)
    
    # Agar foydalanuvchi ishtirokchi bo'lmasa, qo'shish
    if not chat_room.participants.filter(id=request.user.id).exists():
        chat_room.participants.add(request.user)
    
    return redirect('chat_room', room_id=chat_room.id)

@login_required
def users_list(request):
    """Foydalanuvchilar ro'yxati (chat uchun)"""
    user = request.user
    
    # Foydalanuvchi roliga qarab ro'yxatni filtrlash
    if user.role == 'student':
        # O'quvchi o'z guruhlari o'qituvchilari va boshqa o'quvchilarini ko'radi
        my_groups = Group.objects.filter(group_students__student=user)
        teachers = User.objects.filter(teaching_groups__in=my_groups).distinct()
        students = User.objects.filter(
            groupstudent__group__in=my_groups
        ).exclude(id=user.id).distinct()
        users = teachers | students
    elif user.role == 'teacher':
        # O'qituvchi o'z guruhlari o'quvchilarini ko'radi
        my_groups = Group.objects.filter(teacher=user)
        users = User.objects.filter(
            groupstudent__group__in=my_groups
        ).distinct()
    elif user.role == 'admin':
        # Admin barchani ko'radi
        users = User.objects.exclude(id=user.id)
    else:
        users = User.objects.none()
    
    return render(request, 'erp/chat/users_list.html', {
        'users': users
    })