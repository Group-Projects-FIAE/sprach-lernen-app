from django.utils import timezone
from vocab.models import VocabularyList, Progress
from django.db.models import Max
from datetime import timedelta

LEARNED_THRESHOLD = 5
LOCK_DAYS = 7


class DashboardService:
    def __init__(self, user):
        self.user = user

    def get_active_lists_with_progress(self):
        active_qs = (self.user.active_lists
                     .all()
                     .prefetch_related('words'))

        results = []
        for vlist in active_qs:
            total_words = vlist.words.count()

            # mastered: words that reached the learned threshold
            learned_words = Progress.objects.filter(
                user=self.user,
                word__vocab_list=vlist,
                correct_count__gte=LEARNED_THRESHOLD
            ).count()

            in_progress_words = Progress.objects.filter(
                user=self.user,
                word__vocab_list=vlist,
                correct_count__gt=0,
                correct_count__lt=LEARNED_THRESHOLD
            ).count()

            # progress percent shows fraction of words learned (mastered)
            progress_percent = round((learned_words / total_words) * 100, 1) if total_words > 0 else 0.0
            is_completed = (0 < total_words == learned_words)

            # determine lock state: if all words learned -> locked until last_learned + LOCK_DAYS
            is_locked = False
            unlock_in_days = 0
            if total_words > 0 and learned_words == total_words:
                last_learned = Progress.objects.filter(
                    user=self.user, word__vocab_list=vlist, correct_count__gte=LEARNED_THRESHOLD
                ).aggregate(max_date=Max('last_correct'))['max_date']
                if last_learned:
                    next_available = last_learned + timedelta(days=LOCK_DAYS)
                    today = timezone.localdate()
                    delta = (next_available - today).days
                    if delta > 0:
                        is_locked = True
                        unlock_in_days = delta

            results.append({
                "id": vlist.id,
                "name": vlist.name,
                "total_words": total_words,
                "learned_words": learned_words,
                "in_progress_words": in_progress_words,
                "progress_percent": progress_percent,
                "is_completed": is_completed,
                "is_locked": is_locked,
                "unlock_in_days": unlock_in_days,
            })

        return results

    def get_today_progress(self):
        today = timezone.localdate()
        # count only those that reached mastery today
        return Progress.objects.filter(
            user=self.user,
            last_correct=today,
            correct_count__gte=LEARNED_THRESHOLD,
        ).count()

    def get_daily_goal(self):
        return self.user.daily_target

    def get_lists_summary(self, active_lists):

        lists_total = VocabularyList.objects.count()
        lists_learned = sum(1 for item in active_lists if item["is_completed"])

        return {
            "lists_total": lists_total,
            "lists_learned": lists_learned,
        }

    def get_dashboard_context(self):

        active_lists = self.get_active_lists_with_progress()
        lists_summary = self.get_lists_summary(active_lists)

        return {
            "started_lists": active_lists,
            "words_today": self.get_today_progress(),
            "words_goal": self.get_daily_goal(),
            "lists_learned": lists_summary["lists_learned"],
            "lists_total": lists_summary["lists_total"],
            "total_points": int(self.user.progress_total),
        }
