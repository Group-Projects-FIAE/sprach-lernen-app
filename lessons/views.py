from django.shortcuts import render, get_object_or_404, redirect

from vocab.models import VocabularyList, Word, Progress
from .lesson_service import LessonService, LEARNED_THRESHOLD


def lesson_input(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)

    # Keep a stable word list for the lesson session in the user's session
    session_key = f"lesson_words_{request.user.pk}_{pk}"
    if request.method == "POST":
        requested_index = int(request.POST.get("word_index", 0))
    else:
        requested_index = int(request.GET.get("word", 0))

    # initialize session word ids on GET (start of session)
    if request.method != "POST" and session_key not in request.session:
        ids = [w.pk for w in service.get_words()]
        request.session[session_key] = ids

    ids = request.session.get(session_key)
    if not ids:
        # fallback to current active words if session missing or empty
        ids = [w.pk for w in service.get_words()]
        # persist rebuilt ids so subsequent requests use updated set
        request.session[session_key] = ids

    # fetch words preserving original order in ids
    in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
    words_now = [in_bulk[i] for i in ids if i in in_bulk]
    total_words = len(words_now)
    if total_words == 0:
        # try to rebuild from current service.get_words() in case some words were mastered
        rebuilt_ids = [w.pk for w in service.get_words()]
        if rebuilt_ids:
            request.session[session_key] = rebuilt_ids
            ids = rebuilt_ids
            in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
            words_now = [in_bulk[i] for i in ids if i in in_bulk]
            total_words = len(words_now)
        if total_words == 0:
            # no active words left — clear session and finish
            if session_key in request.session:
                del request.session[session_key]
            return render(request, "lessons/finished.html")

    # clamp requested index into bounds
    if requested_index < 0:
        current_index = 0
    elif requested_index >= total_words:
        current_index = total_words - 1
    else:
        current_index = requested_index

    word = words_now[current_index]
    # no upcoming list needed in context (UI removed)

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
                context["feedback"] = "Richtig! 🎉"
                context["feedback_class"] = "correct"
                service.update_progress(word, True)
                # Do NOT redirect here — render the same template with feedback visible.
                # Include the typed answer so it remains visible in the (disabled) input.
                context["user_answer"] = raw_answer
                # The template already supports a 'Next' action; user presses Next to continue.
                return render(request, "lessons/input.html", context)

            else:
                context["feedback"] = "Leider falsch."
                context["feedback_class"] = "incorrect"
                context["correct_answer"] = word.translation
                service.update_progress(word, False)

        elif action == "skip":
            # allow skipping to a chosen upcoming word via POST 'skip_to'
            skip_to = request.POST.get('skip_to')
            try:
                if skip_to:
                    next_index = int(skip_to)
                else:
                    next_index = current_index + 1
            except (TypeError, ValueError):
                next_index = current_index + 1
            # finish only if we advanced past last item
            if next_index >= total_words:
                # attempt to rebuild the session word list (some words might have been removed after mastery)
                rebuilt_ids = [w.pk for w in service.get_words()]
                if rebuilt_ids:
                    request.session[session_key] = rebuilt_ids
                    ids = rebuilt_ids
                    in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
                    words_now = [in_bulk[i] for i in ids if i in in_bulk]
                    total_words = len(words_now)
                    # clamp next_index into new range
                    if next_index >= total_words:
                        # still past the end -> finish
                        if session_key in request.session:
                            del request.session[session_key]
                        return render(request, "lessons/finished.html")
                else:
                    if session_key in request.session:
                        del request.session[session_key]
                    return render(request, "lessons/finished.html")
            # clamp to valid range
            if next_index < 0:
                next_index = 0
            return redirect(f"{request.path}?word={next_index}")

        elif action == "next":
            # Move to next index in the session sequence; finish only when passing last
            next_index = current_index + 1
            if next_index >= total_words:
                # attempt rebuild before finishing
                rebuilt_ids = [w.pk for w in service.get_words()]
                if rebuilt_ids:
                    request.session[session_key] = rebuilt_ids
                    ids = rebuilt_ids
                    in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
                    words_now = [in_bulk[i] for i in ids if i in in_bulk]
                    total_words = len(words_now)
                    if next_index >= total_words:
                        if session_key in request.session:
                            del request.session[session_key]
                        return render(request, "lessons/finished.html")
                else:
                    if session_key in request.session:
                        del request.session[session_key]
                    return render(request, "lessons/finished.html")
            return redirect(f"{request.path}?word={next_index}")

    return render(request, "lessons/input.html", context)

def lesson_select(request, pk):
    vocab_list = get_object_or_404(VocabularyList, pk=pk)
    service = LessonService(request.user, vocab_list)

    # session key same as above
    session_key = f"lesson_words_{request.user.pk}_{pk}"
    if request.method == "POST":
        requested_index = int(request.POST.get("word_index", request.GET.get("word", 0)))
    else:
        requested_index = int(request.GET.get("word", 0))

    if request.method != "POST" and session_key not in request.session:
        request.session[session_key] = [w.pk for w in service.get_words()]

    ids = request.session.get(session_key) or [w.pk for w in service.get_words()]
    # persist if we rebuilt from service.get_words()
    if session_key not in request.session:
        request.session[session_key] = ids
    in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
    words_now = [in_bulk[i] for i in ids if i in in_bulk]
    total_words = len(words_now)
    if total_words == 0:
        # attempt rebuild from service.get_words()
        rebuilt_ids = [w.pk for w in service.get_words()]
        if rebuilt_ids:
            request.session[session_key] = rebuilt_ids
            ids = rebuilt_ids
            in_bulk = vocab_list.words.filter(pk__in=ids).in_bulk()
            words_now = [in_bulk[i] for i in ids if i in in_bulk]
            total_words = len(words_now)
        if total_words == 0:
            if session_key in request.session:
                del request.session[session_key]
            return render(request, "lessons/finished.html")
    if requested_index < 0:
        current_index = 0
    elif requested_index >= total_words:
        current_index = total_words - 1
    else:
        current_index = requested_index

    word = words_now[current_index]
    # no upcoming list needed in context (UI removed)

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
                        # ensure session still valid after updating progress (a word might become mastered and be filtered)
                        rebuilt_ids = [w.pk for w in service.get_words()]
                        if rebuilt_ids and rebuilt_ids != request.session.get(session_key):
                            request.session[session_key] = rebuilt_ids
                            # do not auto-advance; re-render with feedback so user presses Next

                        # mark as checked and keep the selected index so template shows the state
                        # Build context and render the template so user sees the feedback and can press Next
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
                            "checked": True,
                        }
                        return render(request, "lessons/select.html", context)
                    else:
                        feedback = "Leider falsch."
                        feedback_class = "incorrect"
                        service.update_progress(word, False)
        elif action == "skip":
            skip_to = request.POST.get('skip_to')
            try:
                if skip_to:
                    next_index = int(skip_to)
                else:
                    next_index = current_index + 1
            except (TypeError, ValueError):
                next_index = current_index + 1
            if next_index >= total_words:
                if session_key in request.session:
                    del request.session[session_key]
                return render(request, "lessons/finished.html")
            if next_index < 0:
                next_index = 0
            return redirect(f"{request.path}?word={next_index}")
        elif action == "next":
            next_index = current_index + 1
            if next_index >= total_words:
                if session_key in request.session:
                    del request.session[session_key]
                return render(request, "lessons/finished.html")
            return redirect(f"{request.path}?word={next_index}")

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