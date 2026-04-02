import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

GITHUB_ISSUES_URL = (
    "https://api.github.com/repos/nicolasdeclerck/test-squad-automation/issues"
)


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
        issues = []
        api_error = False
        try:
            response = requests.get(
                GITHUB_ISSUES_URL,
                params={"state": "open"},
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            if response.status_code == 200:
                issues = [
                    {
                        "title": issue["title"],
                        "labels": [
                            {"name": label["name"], "color": label["color"]}
                            for label in issue.get("labels", [])
                        ],
                    }
                    for issue in response.json()
                ]
            else:
                api_error = True
        except requests.RequestException:
            api_error = True
        context["issues"] = issues
        context["api_error"] = api_error
        return context
