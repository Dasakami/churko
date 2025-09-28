from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models


class District(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
        ('epic', 'Эпическая'),
    ]
    STATUS = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В процессе'),
        ('waiting', 'Ожидает'),
        ('completed', 'Завершена'),
    ]
    name = models.CharField(max_length=100, unique=True)  
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="districts/", blank=True, storage=MediaCloudinaryStorage())
    status = models.CharField(max_length=20, choices=STATUS, default='not_started')
    is_active = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    short_desc = models.CharField(max_length=350)

    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Районы'

    def __str__(self):
        return self.name

class Level(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
        ('epic', 'Эпическая'),
    ]
    
    STATUS = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В процессе'),
        ('waiting', 'Ожидает'),
        ('completed', 'Завершена'),
    ]
    CHOICES_DOSTUP = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В процессе'),
        ('waiting', 'Ожидает'),
        ('completed', 'Завершена'),
    ]
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='not_started')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    district = models.ForeignKey(District,  on_delete=models.CASCADE, related_name='levels')
    is_active = models.BooleanField(default=True)
    total_time = models.IntegerField(default=600)
    coins = models.IntegerField(default=50)
    gems = models.IntegerField(default=5)
    max_humans = models.IntegerField(default=5)
    image = models.ImageField(upload_to='levels/',  blank=True, storage=MediaCloudinaryStorage())
    dostup = models.CharField(max_length=150, choices=CHOICES_DOSTUP, default='not_started')
    icon = models.CharField(max_length=50)


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Уровень'
        verbose_name_plural = 'Уровни'

class Task(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    text = models.TextField()
    correct_code = models.CharField(max_length=50)
    order = models.IntegerField() 
    time_limit = models.IntegerField(default=120)  
    image = models.ImageField(upload_to='levels/tasks/',  blank=True, storage=MediaCloudinaryStorage())

    def __str__(self):
        return f"{self.level.name} — Задача {self.order}"
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
