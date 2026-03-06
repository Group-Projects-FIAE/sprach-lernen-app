from django.db import models
from django.contrib.auth.models import AbstractUser
from vocab.models import LanguageLevel

class User(AbstractUser):
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True)
    level = models.ForeignKey('vocab.LanguageLevel', on_delete=models.SET_NULL, blank=True, null=True)
    daily_target = models.PositiveIntegerField(default=10)
    progress_total = models.FloatField(default=0)
    progress_daily = models.FloatField(default=0)
    custom_lists = models.ManyToManyField('vocab.VocabularyList', blank=True, related_name='custom_of')
    active_lists = models.ManyToManyField('vocab.VocabularyList', blank=True, related_name='active_of')

    def __str__(self):
        return f"{self.username} ({self.level})"