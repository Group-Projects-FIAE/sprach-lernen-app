from django.shortcuts import render
import random


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
    return render(request, "dashboard/dashboard.html", context)


def lesson_input(request):
    """View für eine Lektion mit Eingabefeld"""
    words = [
        {'german': 'Haus', 'english': 'House', 'hint': 'Ein Gebäude zum Wohnen'},
        {'german': 'Baum', 'english': 'Tree', 'hint': 'Wächst im Wald'},
        {'german': 'Wasser', 'english': 'Water', 'hint': 'H2O'},
    ]

    current_index = int(request.GET.get('word', 0))
    if current_index >= len(words):
        current_index = 0

    word = words[current_index]
    total_words = len(words)
    progress = int((current_index / total_words) * 100)

    context = {
        'word': word,
        'current_word': current_index + 1,
        'total_words': total_words,
        'progress': progress,
        'feedback': None,
        'feedback_class': '',
        'correct_answer': None,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        user_answer = request.POST.get('answer', '').strip().lower()

        if action == 'check':
            correct = word['english'].lower()
            if user_answer == correct:
                context['feedback'] = 'Richtig! 🎉'
                context['feedback_class'] = 'correct'
            else:
                context['feedback'] = 'Leider falsch.'
                context['feedback_class'] = 'incorrect'
                context['correct_answer'] = word['english']
        elif action == 'skip':
            context['feedback'] = 'Übersprungen'
            context['feedback_class'] = 'incorrect'
            context['correct_answer'] = word['english']

    return render(request, "lessons/input.html", context)


def lesson_select(request):
    """View für eine Multiple-Choice-Lektion mit 4 Auswahlkarten"""
    # Beispieldaten - später aus der Datenbank laden
    words = [
        {
            'german': 'Haus',
            'english': 'House',
            'hint': 'Ein Gebäude zum Wohnen',
            'wrong_options': ['Tree', 'Car', 'Book']
        },
        {
            'german': 'Baum',
            'english': 'Tree',
            'hint': 'Wächst im Wald',
            'wrong_options': ['House', 'Water', 'Sun']
        },
        {
            'german': 'Wasser',
            'english': 'Water',
            'hint': 'H2O',
            'wrong_options': ['Fire', 'Earth', 'Air']
        },
    ]

    # Aktuelles Wort (später mit Session verwalten)
    current_index = int(request.GET.get('word', 0))
    if current_index >= len(words):
        current_index = 0

    word = words[current_index]
    total_words = len(words)
    progress = int((current_index / total_words) * 100)

    # Optionen erstellen (1 richtige + 3 falsche)
    options = [{'id': 1, 'text': word['english'], 'correct': True}]
    for i, wrong in enumerate(word['wrong_options'], start=2):
        options.append({'id': i, 'text': wrong, 'correct': False})

    # Optionen mischen
    random.shuffle(options)

    # Richtige ID finden
    correct_id = next(opt['id'] for opt in options if opt['correct'])

    context = {
        'word': word,
        'options': options,
        'current_word': current_index + 1,
        'total_words': total_words,
        'progress': progress,
        'feedback': None,
        'feedback_class': '',
        'selected': None,
        'correct_id': correct_id,
    }

    # POST-Request verarbeiten (Antwort prüfen)
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_id = request.POST.get('answer')

        if selected_id:
            selected_id = int(selected_id)
            context['selected'] = selected_id

        if action == 'check':
            if selected_id == correct_id:
                context['feedback'] = 'Richtig! 🎉'
                context['feedback_class'] = 'correct'
            else:
                context['feedback'] = 'Leider falsch. Die richtige Antwort ist markiert.'
                context['feedback_class'] = 'incorrect'
        elif action == 'skip':
            context['feedback'] = 'Übersprungen. Die richtige Antwort ist markiert.'
            context['feedback_class'] = 'incorrect'

    return render(request, "lessons/select.html", context)

