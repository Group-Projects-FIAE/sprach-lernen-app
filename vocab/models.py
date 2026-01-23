from django.db import models
from django.conf import settings

class LanguageLevel(models.Model):
    code = models.CharField(max_length=5, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.code

class VocabularyList(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_system = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Word(models.Model):
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=200)
    vocab_list = models.ForeignKey(VocabularyList, on_delete=models.CASCADE, related_name='words')

    def __str__(self):
        return self.word

class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    level = models.ForeignKey(LanguageLevel, on_delete=models.SET_NULL, null=True)
    correct_count = models.PositiveIntegerField(default=0)
    last_correct = models.DateField(null=True, blank=True)
    next_review = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} -  {self.word.word} ({self.correct_count})"