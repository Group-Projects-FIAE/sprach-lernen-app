from django.db import models
from vocab.models import LanguageLevel, VocabularyList

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)
    vocab_list = models.ForeignKey(VocabularyList, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.level.code}"
