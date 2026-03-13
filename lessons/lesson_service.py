import random
from datetime import timedelta

from django.utils import timezone

from vocab.models import  Progress

LEARNED_THRESHOLD = 5
REVIEW_DAYS = 14


class LessonService:
    def __init__(self, user, vocab_list):
        self.user = user
        self.vocab_list = vocab_list

    def get_words(self):
        today = timezone.localdate()
        words = self.vocab_list.words.all().order_by('word')

        # Виключаємо вивчені слова (повтор через 2 тижні)
        return [
            w for w in words
            if not Progress.objects.filter(
                user=self.user,
                word=w,
                correct_count__gte=LEARNED_THRESHOLD,
                last_correct__gt=today - timedelta(days=REVIEW_DAYS)
            ).exists()
        ]

    def get_word(self, index):
        words = self.get_words()
        total_words = len(words)
        if index >= total_words:
            return None, total_words
        return words[index], total_words

    def get_options(self, word):
        all_words = list(self.vocab_list.words.exclude(pk=word.pk))
        import random
        wrong_words = random.sample(all_words, min(3, len(all_words)))
        options = [{"text": word.translation, "correct": True}] + [
            {"text": w.translation, "correct": False} for w in wrong_words
        ]
        random.shuffle(options)
        return options

    def update_progress(self, word, correct):
        p, created = Progress.objects.get_or_create(user=self.user, word=word)
        if correct:
            p.correct_count += 1
            p.last_correct = timezone.localdate()
        p.save()
