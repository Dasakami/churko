from django.urls import path, include
from . import views

urlpatterns = [
    path('create/<int:level_id>/', views.create_room, name='create_room'),
    path('<int:room_id>/add/', views.add_member, name='add_member'),
    path('<int:room_id>/play/', views.play_room, name='play_room'),
    path('room/invite/<int:room_id>/', views.create_room_invite_link, name='create_room_invite_link'),
    path('room/join/<uuid:token>/', views.join_room_by_link, name='join_room_by_link'),

]
