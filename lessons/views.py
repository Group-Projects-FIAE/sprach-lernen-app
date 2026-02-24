from django.shortcuts import render
from .models import VocabularyList


def dashboard(request):
    user = request.user
    started_lists = VocabularyList.objects.all()

    words_today = user.progress_daily
    words_goal = user.daily_target

    context = {
        "started_lists": started_lists,
        "words_today": words_today,
        "words_goal": words_goal,
        "lists_learned": started_lists.count(),
        "lists_total": VocabularyList.objects.count(),
    }
    return render(request, "dashboard/dashboard.html", context)
