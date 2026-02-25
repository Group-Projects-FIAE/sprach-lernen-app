from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import DashboardService


class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = DashboardService(self.request.user)
        context.update(service.get_dashboard_context())
        return context

