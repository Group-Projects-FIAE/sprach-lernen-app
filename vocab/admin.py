from django.contrib import admin
from .models import Language, LanguageLevel, VocabularyList, Word, Progress

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(LanguageLevel)
class LanguageLevelAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')


class WordInline(admin.TabularInline):
    model = Word
    extra = 0
    fields = ('word', 'translation', 'word_type')


@admin.register(VocabularyList)
class VocabularyListAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'language', 'is_system', 'created_by', 'word_count')
    list_filter = ('level', 'is_system')
    inlines = [WordInline]

    def word_count(self, obj):
        return obj.words.count()
    word_count.short_description = 'Words'


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'word_type', 'vocab_list')
    list_filter = ('vocab_list__level', 'word_type')
    search_fields = ('word', 'translation')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'correct_count', 'last_correct', 'next_review')
    list_filter = ('user', 'level')
