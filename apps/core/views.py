from django.views.generic import TemplateView


class ComingSoonView(TemplateView):
    template_name = "core/coming_soon.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Coming Soon"
        context["meta_description"] = (
            "Notre blog arrive bientôt. Restez connectés !"
        )
        return context
