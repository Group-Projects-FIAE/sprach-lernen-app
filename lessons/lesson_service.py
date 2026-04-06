import random

from django.utils import timezone

from sprachlernen.constants import LEARNED_THRESHOLD
from vocab.models import Progress


def get_session_key(user_pk, vocab_list_pk):
    """Generate consistent session key for lesson word list."""
    return f"lesson_words_{user_pk}_{vocab_list_pk}"


def clamp_index(index, total):
    """Clamp index to valid range [0, total-1]."""
    if index < 0:
        return 0
    if index >= total:
        return total - 1
    return index


class LessonService:
    def __init__(self, user, vocab_list):
        self.user = user
        self.vocab_list = vocab_list

    def get_words(self):
        # Active words are those that have NOT yet reached the learned threshold
        words = self.vocab_list.words.all().order_by('word')

        return [
            w for w in words
            if not Progress.objects.filter(
                user=self.user,
                word=w,
                correct_count__gte=LEARNED_THRESHOLD,
            ).exists()
        ]

    def get_options(self, word):
        all_words = list(self.vocab_list.words.exclude(pk=word.pk))
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
            # User points system
            self.user.progress_total += 1
            self.user.save()
        p.save()
