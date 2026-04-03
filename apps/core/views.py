from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from apps.core.services import fetch_github_issues


class ComingSoonView(TemplateView):
    template_name = "core/coming_soon.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Coming Soon"
        context["meta_description"] = (
            "Notre blog arrive bientôt. Restez connectés !"
        )
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


class DevTrackingView(LoginRequiredMixin, TemplateView):
    template_name = "core/dev_tracking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Suivi des devs"
        context["meta_description"] = (
            "Suivez l'avancement des développements en cours."
        )
        issues, context["api_error"] = fetch_github_issues()
        paginator = Paginator(issues, 10)
        page_number = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(page_number)
        context["issues"] = context["page_obj"].object_list
        return context
