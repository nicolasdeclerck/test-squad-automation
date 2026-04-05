from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Comment, Post


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author__profile")
            .order_by("-created_at")[:10]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Blog"
        context["meta_description"] = (
            "Découvrez les derniers articles de notre blog."
        )
        total = Post.objects.filter(status=Post.STATUS_PUBLISHED).count()
        context["show_full_list_link"] = total > 10
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ajouter un article"
        context["meta_description"] = (
            "Créez un nouvel article sur le blog."
        )
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("home")
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Modifier l'article"
        context["meta_description"] = (
            "Modifiez votre article sur le blog."
        )
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home")
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Supprimer l'article"
        context["meta_description"] = (
            "Confirmez la suppression de votre article."
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author__profile")
            .prefetch_related("comments__author__profile")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        context["meta_description"] = (
            self.object.content[:160]
        )
        context["approved_comments"] = (
            self.object.comments.filter(is_approved=True)
            .select_related("author__profile")
            .order_by("-created_at")
        )
        if self.request.user.is_authenticated:
            context["comment_form"] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(
            Post, slug=self.kwargs["slug"], status=Post.STATUS_PUBLISHED
        )
        form.instance.author = self.request.user
        form.instance.post = post
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Votre commentaire a été soumis et est en attente de modération.",
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Le commentaire n'a pas pu être soumis. Veuillez corriger les erreurs.",
        )
        return redirect(
            reverse("post_detail", kwargs={"slug": self.kwargs["slug"]})
        )

    def get_success_url(self):
        return reverse("post_detail", kwargs={"slug": self.kwargs["slug"]})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse("post_detail", kwargs={"slug": self.kwargs["slug"]})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Votre commentaire a été supprimé.")
        return response

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("author__profile")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tous les articles"
        context["meta_description"] = (
            "Liste complète des articles du blog."
        )
        return context
