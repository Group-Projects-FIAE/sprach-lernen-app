from .models import VocabularyList

def nav_lists(request):
    system_lists = VocabularyList.objects.filter(is_system=True)
    custom_lists = []
    if request.user.is_authenticated:
        custom_lists = VocabularyList.objects.filter(is_system=False, created_by=request.user)
    
    return {
        'system_lists': system_lists,
        'custom_lists': custom_lists,
    }
