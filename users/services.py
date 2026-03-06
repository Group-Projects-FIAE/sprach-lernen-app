from django.utils import timezone
from vocab.models import VocabularyList, Progress

LEARNED_THRESHOLD = 5


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

            progress_percent = round((learned_words / total_words) * 100, 1) if total_words > 0 else 0.0
            is_completed = (0 < total_words == learned_words)

            results.append({
                "id": vlist.id,
                "name": vlist.name,
                "total_words": total_words,
                "learned_words": learned_words,
                "in_progress_words": in_progress_words,
                "progress_percent": progress_percent,
                "is_completed": is_completed,
            })

        return results

    def get_today_progress(self):
        today = timezone.localdate()
        return Progress.objects.filter(
            user=self.user,
            last_correct=today
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
        }

