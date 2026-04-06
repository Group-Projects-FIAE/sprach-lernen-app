from django.shortcuts import render, get_object_or_404, redirect

from vocab.models import VocabularyList
from .lesson_service import LessonService, get_session_key, clamp_index


def _get_lesson_words(request, service, vocab_list, session_key):
    """
    Get or initialize the word list for a lesson session.
    Returns (words_list, total_words) or (None, 0) if no words.
    """
    # Initialize session on first GET
    if request.method != "POST" and session_key not in request.session:
        request.session[session_key] = [w.pk for w in service.get_words()]

    ids = request.session.get(session_key)
    if not ids:
        ids = [w.pk for w in service.get_words()]
        request.session[session_key] = ids

    # Fetch words preserving order
    in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
    words_now = [in_bulk[i] for i in ids if i in in_bulk]
    total_words = len(words_now)

    # Attempt rebuild if empty
    if total_words == 0:
        rebuilt_ids = [w.pk for w in service.get_words()]
        if rebuilt_ids:
            request.session[session_key] = rebuilt_ids
            in_bulk = vocab_list.words.filter(pk__in=rebuilt_ids).in_bulk()
            words_now = [in_bulk[i] for i in rebuilt_ids if i in in_bulk]
            total_words = len(words_now)

    return words_now, total_words


def _handle_lesson_navigation(request, action, current_index, total_words, session_key):
    """
    Handle skip/next navigation actions.
    Returns redirect URL or None if lesson should finish.
    """
    if action == "skip":
        skip_to = request.POST.get('skip_to')
        try:
            next_index = int(skip_to) if skip_to else current_index + 1
        except (TypeError, ValueError):
            next_index = current_index + 1
    else:  # next
        next_index = current_index + 1

    if next_index >= total_words:
        if session_key in request.session:
            del request.session[session_key]
        return None  # Signal to finish lesson

    if next_index < 0:
        next_index = 0
    return f"{request.path}?word={next_index}"


def lesson_input(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)
    session_key = get_session_key(request.user.pk, pk)

    if request.method == "POST":
        requested_index = int(request.POST.get("word_index", 0))
    else:
        requested_index = int(request.GET.get("word", 0))

    words_now, total_words = _get_lesson_words(request, service, vocab_list, session_key)

    if total_words == 0:
        if session_key in request.session:
            del request.session[session_key]
        return render(request, "lessons/finished.html")

    current_index = clamp_index(requested_index, total_words)
    word = words_now[current_index]

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
        raw_answer = request.POST.get("answer", "").strip()
        user_answer = raw_answer.lower()
        # expose the raw typed answer to the template so the input can display it
        context["user_answer"] = raw_answer
        correct = word.translation.lower()

        if action == "check":
            context["checked"] = True

            if user_answer == correct:
                # Provide immediate feedback and stay on the same page so the user sees the result.
                context["feedback"] = "correct 🎉"
                context["feedback_class"] = "correct"
                service.update_progress(word, True)
                # Do NOT redirect here — render the same template with feedback visible.
                # Include the typed answer so it remains visible in the (disabled) input.
                context["user_answer"] = raw_answer
                # The template already supports a 'Next' action; user presses Next to continue.
                return render(request, "lessons/input.html", context)

            else:
                context["feedback"] = "incorrect"
                context["feedback_class"] = "incorrect"
                context["correct_answer"] = word.translation
                service.update_progress(word, False)

        elif action in ("skip", "next"):
            nav_url = _handle_lesson_navigation(request, action, current_index, total_words, session_key)
            if nav_url is None:
                return render(request, "lessons/finished.html")
            return redirect(nav_url)

    return render(request, "lessons/input.html", context)


def lesson_select(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)
    session_key = get_session_key(request.user.pk, pk)

    if request.method == "POST":
        requested_index = int(request.POST.get("word_index", request.GET.get("word", 0)))
    else:
        requested_index = int(request.GET.get("word", 0))

    words_now, total_words = _get_lesson_words(request, service, vocab_list, session_key)

    if total_words == 0:
        if session_key in request.session:
            del request.session[session_key]
        return render(request, "lessons/finished.html")

    current_index = clamp_index(requested_index, total_words)
    word = words_now[current_index]

    if not word:
        return render(request, "lessons/finished.html")

    if request.method == "GET":
        options = service.get_options(word)
        request.session[f"options_{current_index}"] = options
    else:
        options = request.session.get(f"options_{current_index}", service.get_options(word))

    feedback = None
    feedback_class = ""
    selected = None
    checked = False

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "check":
            ans = request.POST.get("answer")
            if ans is None or ans == "":
                # No selection made — inform user instead of crashing
                feedback = "Please choose an option before checking."
                feedback_class = "incorrect"
                checked = False
            else:
                try:
                    selected = int(ans)
                except (TypeError, ValueError):
                    feedback = "Invalid selection. Please try again."
                    feedback_class = "incorrect"
                    checked = False
                else:
                    checked = True
                    if options[selected]["correct"]:
                        # Correct answer: show feedback on the same page instead of immediate redirect
                        feedback = "Correct! 🎉"
                        feedback_class = "correct"
                        service.update_progress(word, True)
                        context = {
                            "word": word,
                            "options": options,
                            "progress": int((current_index / total_words) * 100),
                            "current_word": current_index + 1,
                            "total_words": total_words,
                            "feedback": feedback,
                            "feedback_class": feedback_class,
                            "selected": selected,
                            "checked": True,
                        }
                        return render(request, "lessons/select.html", context)
                    else:
                        feedback = "incorrect"
                        feedback_class = "incorrect"
                        service.update_progress(word, False)
        elif action in ("skip", "next"):
            nav_url = _handle_lesson_navigation(request, action, current_index, total_words, session_key)
            if nav_url is None:
                return render(request, "lessons/finished.html")
            return redirect(nav_url)

    context = {
        "word": word,
        "options": options,
        "progress": int((current_index / total_words) * 100),
        "current_word": current_index + 1,
        "total_words": total_words,
        "feedback": feedback,
        "feedback_class": feedback_class,
        "selected": selected,
        "checked": checked,
    }

    return render(request, "lessons/select.html", context)