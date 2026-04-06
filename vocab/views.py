from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Subquery, OuterRef, IntegerField, Value, Max
from django.db.models.functions import Coalesce
from .models import LanguageLevel, VocabularyList, Word, Progress
from django.views import View
from django.utils import timezone
from datetime import timedelta

LEARNED_THRESHOLD = 5
LOCK_DAYS = 7

class VocabListView(LoginRequiredMixin, ListView):
    model = VocabularyList
    template_name = 'vocab/lists.html'
    context_object_name = 'system_lists'

    def get_queryset(self):
        level = self.request.GET.get('level')
        qs = VocabularyList.objects.filter(is_system=True).select_related('level')
        if level:
            qs = qs.filter(level__code=level)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        level = self.request.GET.get('level')
        today = timezone.localdate()
        custom_qs = VocabularyList.objects.filter(created_by=self.request.user, is_system=False).select_related('level')
        if level:
            custom_qs = custom_qs.filter(level__code=level)
        # build metrics for custom lists
        custom_lists_with_metrics = []
        for vlist in custom_qs:
            total_words = vlist.words.count()
            # number of words that reached the learned threshold
            learned_count = Progress.objects.filter(
                user=self.request.user, word__vocab_list=vlist, correct_count__gte=LEARNED_THRESHOLD
            ).count()
            # Count only learned words (correct_count >= LEARNED_THRESHOLD)
            learned_all = learned_count
            # Count only those mastered today
            learned_today = Progress.objects.filter(
                user=self.request.user,
                word__vocab_list=vlist,
                last_correct=today,
                correct_count__gte=LEARNED_THRESHOLD,
            ).count()
            progress_percent = round((learned_all / total_words) * 100, 1) if total_words > 0 else 0.0
            # determine lock state: if all words learned -> locked until last_learned + LOCK_DAYS
            is_locked = False
            unlock_in_days = 0
            if total_words > 0 and learned_count == total_words:
                last_learned = Progress.objects.filter(
                    user=self.request.user, word__vocab_list=vlist, correct_count__gte=LEARNED_THRESHOLD
                ).aggregate(max_date=Max('last_correct'))['max_date']
                if last_learned:
                    next_available = last_learned + timedelta(days=LOCK_DAYS)
                    delta = (next_available - today).days
                    if delta > 0:
                        is_locked = True
                        unlock_in_days = delta

            custom_lists_with_metrics.append({
                'pk': vlist.pk,
                'name': vlist.name,
                'total_words': total_words,
                'learned_words': learned_all,
                'learned_today': learned_today,
                'progress_percent': progress_percent,
                'is_locked': is_locked,
                'unlock_in_days': unlock_in_days,
            })
        # keep original 'custom_lists' name for compatibility; expose metrics under a different key
        context['custom_lists_metrics'] = custom_lists_with_metrics
        context['current_level'] = level
        context['levels'] = LanguageLevel.objects.all().order_by('code')
        # also adapt system lists from queryset returned by get_queryset
        system_qs = context.get('system_lists')
        system_lists_with_metrics = []
        for vlist in system_qs:
            total_words = vlist.words.count()
            # number of words that reached the learned threshold
            learned_count = Progress.objects.filter(user=self.request.user, word__vocab_list=vlist, correct_count__gte=LEARNED_THRESHOLD).count()
            learned_all = learned_count
            learned_today = Progress.objects.filter(
                user=self.request.user,
                word__vocab_list=vlist,
                last_correct=today,
                correct_count__gte=LEARNED_THRESHOLD,
            ).count()
            progress_percent = round((learned_all / total_words) * 100, 1) if total_words > 0 else 0.0
            # lock state for system lists
            is_locked = False
            unlock_in_days = 0
            if total_words > 0 and learned_count == total_words:
                last_learned = Progress.objects.filter(
                    user=self.request.user, word__vocab_list=vlist, correct_count__gte=LEARNED_THRESHOLD
                ).aggregate(max_date=Max('last_correct'))['max_date']
                if last_learned:
                    next_available = last_learned + timedelta(days=LOCK_DAYS)
                    delta = (next_available - today).days
                    if delta > 0:
                        is_locked = True
                        unlock_in_days = delta

            system_lists_with_metrics.append({
                'pk': vlist.pk,
                'name': vlist.name,
                'total_words': total_words,
                'learned_words': learned_all,
                'learned_today': learned_today,
                'progress_percent': progress_percent,
                'is_locked': is_locked,
                'unlock_in_days': unlock_in_days,
            })
        # keep original 'system_lists' (provided by ListView) for global templates; give metrics separately
        context['system_lists_metrics'] = system_lists_with_metrics
        return context

class ListDetailView(LoginRequiredMixin, DetailView):
    model = VocabularyList
    template_name = 'vocab/list_detail.html'
    context_object_name = 'vocab_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocab_list = self.get_object()
        
        # today is used to compute learned_today (mastered today)
        today = timezone.localdate()

        progress_subquery = Progress.objects.filter(
            user=self.request.user, word=OuterRef('pk')
        ).values('correct_count')[:1]

        words = vocab_list.words.annotate(
            progress_count=Coalesce(
                Subquery(progress_subquery, output_field=IntegerField()),
                Value(0)
            )
        ).order_by('word')

        context['words'] = words
        context['total_words'] = words.count()
        # total learned (correct_count >= LEARNED_THRESHOLD)
        learned_all = words.filter(progress_count__gte=LEARNED_THRESHOLD).count()
        learned_today = Progress.objects.filter(
            user=self.request.user,
            word__vocab_list=vocab_list,
            last_correct=today,
            correct_count__gte=LEARNED_THRESHOLD,
        ).count()
        progress_percent = round((learned_all / context['total_words']) * 100, 1) if context['total_words'] > 0 else 0.0
        context['learned_words'] = learned_all
        context['learned_today'] = learned_today
        # compute circle dash offset (same circumference used elsewhere)
        CIRC = 283.0
        # compute using raw fraction to avoid rounding issues
        fraction = (learned_all / context['total_words']) if context['total_words'] > 0 else 0.0
        context['progress_offset'] = max(0.0, min(CIRC, CIRC * (1.0 - fraction)))
        context['progress_percent'] = progress_percent
        return context

class CreateListView(LoginRequiredMixin, CreateView):
    model = VocabularyList
    template_name = 'vocab/create_list.html'
    fields = ['name', 'level']
    
    def get_initial(self):

        initial = super().get_initial()
        if self.request.method == 'GET':
            # if a name query param exists, use it as highest priority
            name_param = self.request.GET.get('name')
            from_id = self.request.GET.get('from')
            if name_param:
                initial['name'] = name_param
            elif from_id:
                try:
                    source_list = VocabularyList.objects.get(pk=from_id)
                    initial['name'] = f"{source_list.name} Copy"
                    initial['level'] = source_list.level_id
                except VocabularyList.DoesNotExist:
                    pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_id = self.request.GET.get('from')
        if from_id:
            try:
                source_list = VocabularyList.objects.get(pk=from_id)
                context['source_list'] = source_list
                context['source_words'] = source_list.words.all().order_by('word')
            except VocabularyList.DoesNotExist:
                pass
        if self.request.method == 'POST':
            try:
                context['selected_word_ids'] = set(int(x) for x in self.request.POST.getlist('words'))
            except (TypeError, ValueError):
                context['selected_word_ids'] = set()
        else:
            context['selected_word_ids'] = set()
        context['system_lists'] = VocabularyList.objects.filter(is_system=True).select_related('level')
        context['levels'] = LanguageLevel.objects.all().order_by('code')
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.is_system = False
        
        # Save the list first
        self.object = form.save()
        
        # Copy words if provided
        word_ids = self.request.POST.getlist('words')
        if word_ids:
            original_words = Word.objects.filter(pk__in=word_ids)
            words_to_create = []
            for w in original_words:
                words_to_create.append(Word(
                    word=w.word,
                    translation=w.translation,
                    vocab_list=self.object,
                    word_type=w.word_type,
                    example=w.example,
                    example_translation=w.example_translation,
                    metadata=w.metadata,
                ))
            Word.objects.bulk_create(words_to_create)
            messages.success(self.request, f'List "{self.object.name}" created with {len(words_to_create)} words.')
        else:
            messages.success(self.request, f'List "{self.object.name}" created.')
            
        # use the shortcut redirect (already imported) to return an HttpResponseRedirect
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('list_detail', kwargs={'pk': self.object.pk})


class DeleteListView(LoginRequiredMixin, DeleteView):
    model = VocabularyList
    success_url = reverse_lazy('vocab_lists')

    def get_queryset(self):
        return VocabularyList.objects.filter(created_by=self.request.user, is_system=False)

    def delete(self, request, *args, **kwargs):
        vocab_list = self.get_object()
        if request.user.active_lists.filter(pk=vocab_list.pk).exists():
            request.user.active_lists.remove(vocab_list)
        messages.success(self.request, 'List deleted.')
        return super().delete(request, *args, **kwargs)

class VocabularyView(LoginRequiredMixin, ListView):
    model = Word
    template_name = 'vocab/vocabulary.html'
    context_object_name = 'words'
    paginate_by = 50

    def get_queryset(self):
        level = self.request.GET.get('level')
        qs = Word.objects.select_related('vocab_list', 'vocab_list__level').order_by('word')
        if level:
            qs = qs.filter(vocab_list__level__code=level)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_level'] = self.request.GET.get('level')
        return context


class StartLessonView(LoginRequiredMixin, View):
    def post(self, request, pk, mode):
        vocab_list = get_object_or_404(VocabularyList, pk=pk)

        # Check if the list is temporarily locked (all words learned and within LOCK_DAYS)
        total_words = vocab_list.words.count()
        if total_words > 0:
            learned_count = Progress.objects.filter(user=request.user, word__vocab_list=vocab_list, correct_count__gte=LEARNED_THRESHOLD).count()
            if learned_count == total_words:
                last_learned = Progress.objects.filter(
                    user=request.user, word__vocab_list=vocab_list, correct_count__gte=LEARNED_THRESHOLD
                ).aggregate(max_date=Max('last_correct'))['max_date']
                if last_learned:
                    next_available = last_learned + timedelta(days=LOCK_DAYS)
                    today = timezone.localdate()
                    if next_available > today:
                        days = (next_available - today).days
                        messages.warning(request, f'This list is locked. Available in {days} days.')
                        return redirect('vocab_lists')

        if vocab_list not in request.user.active_lists.all():
            request.user.active_lists.add(vocab_list)

        if mode == "input":
            return redirect("lesson_input", pk=pk)
        elif mode == "select":
            return redirect("lesson_select", pk=pk)
        else:
            return redirect("vocab_lists")