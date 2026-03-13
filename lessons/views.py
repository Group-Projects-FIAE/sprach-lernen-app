from django.shortcuts import render, get_object_or_404, redirect

from vocab.models import VocabularyList
from .lesson_service import LessonService


def lesson_input(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)

    if request.method == "POST":
        current_index = int(request.POST.get("word_index", 0))
    else:
        current_index = int(request.GET.get("word", 0))

    word, total_words = service.get_word(current_index)

    if not word:
        return render(request, "lessons/finished.html")

    progress_percent = int((current_index / total_words) * 100)

    context = {
        "word": word,
        "current_word": current_index + 1,
        "total_words": total_words,
        "progress": progress_percent,
        "feedback": None,
        "feedback_class": "",
        "correct_answer": None,
        "checked": False,
    }

    if request.method == "POST":

        action = request.POST.get("action")
        user_answer = request.POST.get("answer", "").strip().lower()
        correct = word.translation.lower()

        if action == "check":
            context["checked"] = True

            if user_answer == correct:
                context["feedback"] = "Richtig! 🎉"
                context["feedback_class"] = "correct"
                service.update_progress(word, True)

            else:
                context["feedback"] = "Leider falsch."
                context["feedback_class"] = "incorrect"
                context["correct_answer"] = word.translation
                service.update_progress(word, False)

        elif action == "skip":
            # одразу наступне слово
            next_index = current_index + 1
            word, total_words = service.get_word(next_index)

            if not word:
                return render(request, "lessons/finished.html")

            context = {
                "word": word,
                "current_word": next_index + 1,
                "total_words": total_words,
                "progress": int((next_index / total_words) * 100),
                "feedback": None,
                "feedback_class": "",
                "correct_answer": None,
                "checked": False,
            }

        elif action == "next":
            next_index = current_index + 1
            word, total_words = service.get_word(next_index)

            if not word:
                return render(request, "lessons/finished.html")

            context = {
                "word": word,
                "current_word": next_index + 1,
                "total_words": total_words,
                "progress": int((next_index / total_words) * 100),
                "feedback": None,
                "feedback_class": "",
                "correct_answer": None,
                "checked": False,
            }

    return render(request, "lessons/input.html", context)

def lesson_select(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)

    current_index = int(request.GET.get("word", 0))
    word, total_words = service.get_word(current_index)

    if not word:
        return render(request, "lessons/finished.html")

    if request.method == "GET":
        options = service.get_options(word)
        request.session[f"options_{current_index}"] = options  # зберігаємо в сесії
    else:
        options = request.session.get(f"options_{current_index}", service.get_options(word))

    correct_id = next(i for i, o in enumerate(options) if o["correct"])

    feedback = None
    feedback_class = ""
    selected = None
    checked = False

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "check":
            selected = int(request.POST.get("answer"))
            checked = True

            if options[selected]["correct"]:
                feedback = "Richtig! 🎉"
                feedback_class = "correct"
                service.update_progress(word, True)
            else:
                feedback = "Leider falsch."
                feedback_class = "incorrect"
                service.update_progress(word, False)
        elif action == "skip":
            return redirect(f"{request.path}?word={current_index + 1}")
        elif action == "next":
            return redirect(f"{request.path}?word={current_index + 1}")

    context = {
        "word": word,
        "options": options,
        "correct_id": correct_id,
        "progress": int((current_index / total_words) * 100),
        "current_word": current_index + 1,
        "total_words": total_words,
        "feedback": feedback,
        "feedback_class": feedback_class,
        "selected": selected,
        "checked": checked,
    }

    return render(request, "lessons/select.html", context)