from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from vocab.models import VocabularyList, Progress

LEARNED_THRESHOLD = 5  # скільки правильних відповідей вважаємо "вивченим словом"


def build_active_lists_with_progress(user):
    """
    Повертає список словників по активних списках користувача:
    [
      {
        "id": 11,
        "name": "Food",
        "total_words": 40,
        "learned_words": 25,
        "progress_percent": 62.5,
        "is_completed": False,
      },
      ...
    ]
    """
    # Забираємо активні списки і одразу prefetch'имо слова, щоб уникати N+1
    active_qs = (user.active_lists
                    .all()
                    .prefetch_related('words'))  # words — це related_name з Word.vocab_list

    results = []
    # Щоб порахувати learned по кожному списку без N+1, зробимо один agg по всіх словах списку:
    # Але оскільки нам треба фільтрувати Progress по user і по словах конкретного списку,
    # читаєм просто в циклі, але з дуже простими запитами — це ок для сотень списків.
    for vlist in active_qs:
        total_words = vlist.words.count()

        learned_words = Progress.objects.filter(
            user=user,
            word__vocab_list=vlist,
            correct_count__gte=LEARNED_THRESHOLD
        ).count()

        progress_percent = round((learned_words / total_words) * 100, 1) if total_words > 0 else 0.0
        is_completed = (0 < total_words == learned_words)

        results.append({
            "id": vlist.id,
            "name": vlist.name,
            "total_words": total_words,
            "learned_words": learned_words,
            "progress_percent": progress_percent,
            "is_completed": is_completed,
        })

    return results


@login_required
def dashboard(request):
    user = request.user

    # 1) Активні списки з прогресом
    active_lists = build_active_lists_with_progress(user)

    # 2) Сьогоднішній прогрес по словах (на основі Progress.last_correct == сьогодні)
    today = timezone.localdate()
    words_today = Progress.objects.filter(
        user=user,
        last_correct=today
    ).count()

    # 3) Ціль на день (як у тебе було)
    words_goal = user.daily_target

    # 4) Зведені метрики
    lists_total = VocabularyList.objects.count()
    lists_learned = sum(1 for item in active_lists if item["is_completed"])

    context = {
        "started_lists": active_lists,     # замінимо started_lists на більш точну назву
        "words_today": words_today,
        "words_goal": words_goal,
        "lists_learned": lists_learned,   # скільки активних списків завершено
        "lists_total": lists_total,       # скільки списків загалом в БД
    }
    return render(request, "dashboard/dashboard.html", context)