from django.db import models
from django.conf import settings
from quests.models import Level, Task
import uuid
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Room(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    invite_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"Комната {self.id} — {self.level.name}"
    
    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} в комнате {self.room.id}"
    class Meta:
        verbose_name = 'Участник комнаты'
        verbose_name_plural = "Участники комнат"


class RoomProgress(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='progress')
    current_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    task_index = models.IntegerField(default=0)  
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    task_started_at = models.DateTimeField(auto_now_add=True)
    level_time_limit = models.IntegerField(default=600)
    task_time_limit = models.IntegerField(default=120)

    def time_left_for_level(self):
        elapsed = (timezone.now() - self.started_at).total_seconds()
        return max(0, self.level_time_limit - elapsed)
    
    
    def time_left_for_task(self):
        elapsed = (timezone.now() - self.task_started_at).total_seconds()
        return max(0, self.task_time_limit - elapsed)
    


    def __str__(self):
        return f"Прогресс комнаты {self.room.id}"
    
    class Meta:
        verbose_name = 'Прогресс комнаты'
        verbose_name_plural = 'Прогрессы комнат'


class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.message} от {self.user.username}'
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщении'




class RoomInvite(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invites')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_room_invites')
    receiver_email = models.EmailField(blank=True, null=True)  # можно отправлять по email или None для ссылки
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # уникальная ссылка
    status_choices = [
        ('pending', 'В ожидании'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Приглашение в комнату'
        verbose_name_plural = 'Приглашения в комнаты'

    def accept(self, user):
        if self.status == 'pending':
            self.status = 'accepted'
            RoomMember.objects.create(room=self.room, user=user)
            self.save()


    def decline(self):
        if self.status == 'pending':
            self.status = 'declined'
            self.save()
