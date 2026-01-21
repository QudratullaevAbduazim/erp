# Bu URLlarni urls.py fayliga qo'shing (urlpatterns ro'yxatiga)

    # Chat URLs
from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_message, name='send_message'),
    path('chat/get-messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('chat/create/<int:user_id>/', views.create_private_chat, name='create_private_chat'),
    path('chat/group/<int:group_id>/', views.group_chat, name='group_chat'),
    path('chat/users/', views.users_list, name='users_list'),
    
]