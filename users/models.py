from django.db import models
from django.contrib.auth.models import AbstractUser
from quests.models import Level, District
from cloudinary_storage.storage import MediaCloudinaryStorage

class User(AbstractUser):
    experience = models.IntegerField(default=0)
    experience_needed = models.IntegerField(default=100)
    level = models.IntegerField(default=1)
    coins =  models.IntegerField(default=0)
    gems = models.IntegerField(default=0)
    hints = models.IntegerField(default=3)
    bio = models.CharField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=255)
    avatar  = models.ImageField(upload_to='users/avatars/', storage=MediaCloudinaryStorage(),  blank=True)


    def __str__(self):
        return f'{self.username} Profile'
    
    def get_experience_percentage(self):
        return min((self.experience / self.experience_needed) * 100, 100)
    
    def add_experience(self, amount):
        self.experience += amount

        while self.experience >= self.experience_needed:
            self.level_up()
        self.save()

    def level_up(self, save=True):
        self.experience -= self.experience_needed
        self.level += 1
        self.experience_needed = int(self.experience_needed * 1.5)
        self.gems += 5
        if save:
            self.save()





class FriendShip(models.Model):
    user1 = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"{self.user1.username} - {self.user2.username}"
    
    @classmethod
    def are_friends(cls, user1, user2):
        return cls.objects.filter(
            models.Q(user1=user1, user2=user2) |
            models.Q(user1=user2, user2=user1)
        ).exists()
    @classmethod
    def create_friendship(cls, user1, user2):
        if user1.id > user2.id:
            user1, user2 = user2, user1 
        if not cls.are_friends(user1, user2):
            cls.objects.create(user1=user1, user2=user2)





class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает ответа'),
        ('accepted', 'Принят'),
        ('declined', 'Отклонен'),
    ]

    sender = models.ForeignKey(User, related_name='sender_request', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver_request', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запрос в друзья'
        verbose_name_plural = 'Запросы в друзья'
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"
    
    def accept(self):
        if self.status == 'pending':
            self.status = 'accepted'
            FriendShip.create_friendship(self.sender, self.receiver)
            self.save()
    
    def decline(self):
        if self.status == 'pending':
            self.status = 'declined'
            self.save()


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  
    experience_reward = models.IntegerField(default=0)
    coins_reward = models.IntegerField(default=0)
    gems_reward = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('task_complete', 'Завершение задачи'),
        ('tournament_join', 'Участие в турнире'),
        ('tournament_win', 'Победа в турнире'),
        ('duel_complete', 'Завершение дуэли'),
        ('chest_open', 'Открытие сундука'),
        ('level_up', 'Повышение уровня'),
        ('achievement', 'Получение достижения'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    experience_gained = models.IntegerField(default=0)
    coins_gained = models.IntegerField(default=0)
    gems_gained = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"