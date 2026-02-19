from django.shortcuts import render


def dashboard(request):
    context = {
        'words_today': 25,
        'words_goal': 50,
        'lists_learned': 3,
        'lists_total': 10,
        'started_lists': [
            {'id': 1, 'name': 'Grundwortschatz', 'progress': 60},
            {'id': 2, 'name': 'Verben', 'progress': 30},
        ]
    }
    return render(request, "dashboard/dashboard.html")

def lists(request):
    return render(request, "lists/lists.html")