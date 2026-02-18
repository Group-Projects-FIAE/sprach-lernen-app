from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Subquery, OuterRef, IntegerField, Value
from django.db.models.functions import Coalesce
from .models import LanguageLevel, VocabularyList, Word, Progress

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
        custom_qs = VocabularyList.objects.filter(created_by=self.request.user, is_system=False).select_related('level')
        if level:
            custom_qs = custom_qs.filter(level__code=level)
        context['custom_lists'] = custom_qs
        context['current_level'] = level
        context['levels'] = LanguageLevel.objects.all().order_by('code')
        return context

class ListDetailView(LoginRequiredMixin, DetailView):
    model = VocabularyList
    template_name = 'vocab/list_detail.html'
    context_object_name = 'vocab_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocab_list = self.get_object()
        
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
        context['learned_count'] = words.filter(progress_count__gte=5).count()
        return context

class CreateListView(LoginRequiredMixin, CreateView):
    model = VocabularyList
    template_name = 'vocab/create_list.html'
    fields = ['name', 'level']
    
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
            
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('list_detail', kwargs={'pk': self.object.pk})

class SetActiveListView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'list_detail'

    def post(self, request, *args, **kwargs):
        vocab_list = get_object_or_404(VocabularyList, pk=kwargs['pk'])
        request.user.active_list = vocab_list
        request.user.save(update_fields=['active_list'])
        messages.success(request, f'"{vocab_list.name}" is now your active list.')
        return super().post(request, *args, **kwargs)

class DeleteListView(LoginRequiredMixin, DeleteView):
    model = VocabularyList
    success_url = reverse_lazy('vocab_lists')

    def get_queryset(self):
        return VocabularyList.objects.filter(created_by=self.request.user, is_system=False)

    def delete(self, request, *args, **kwargs):
        vocab_list = self.get_object()
        if request.user.active_list == vocab_list:
            request.user.active_list = None
            request.user.save(update_fields=['active_list'])
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

