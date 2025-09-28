from django.contrib import admin
from .models import Room, RoomMember, RoomProgress, ChatMessage

admin.site.register(Room)
admin.site.register(RoomProgress)
admin.site.register(RoomMember)
admin.site.register(ChatMessage)
# Register your models here.
