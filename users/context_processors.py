"""
Context processor so social account providers are always available in templates.
Fixes "no providers" when get_providers tag doesn't see the right site/request.
"""
import time


def cache_buster(request):
    """Add timestamp for CSS cache busting during development"""
    return {"now": int(time.time())}


def socialaccount_providers(request):
    try:
        from allauth.socialaccount.adapter import get_adapter
        adapter = get_adapter()
        providers = adapter.list_providers(request)
        providers = [
            p for p in providers
            if (not getattr(p, "uses_apps", True) or not (getattr(p, "app", None) and p.app and p.app.settings.get("hidden")))
        ]
        return {"socialaccount_providers": sorted(providers, key=lambda p: p.name)}
    except Exception:
        return {"socialaccount_providers": []}
