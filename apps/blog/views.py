import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.blog.forms import PostForm
from apps.blog.models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author", "category")
            .prefetch_related("tags")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.select_related("author", "category").prefetch_related(
                "tags"
            ),
            slug=self.kwargs["slug"],
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["initial_json"] = json.dumps([])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        if post.author != self.request.user:
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        content_json = post.content_json or []
        context["initial_json"] = json.dumps(content_json)
        return context
