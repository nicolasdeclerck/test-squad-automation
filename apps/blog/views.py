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

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = Post.STATUS_DRAFT
        form.instance.draft_title = form.cleaned_data.get("title", "")
        form.instance.draft_content = form.cleaned_data.get("content", "")
        form.instance.has_draft = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("post_update", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ajouter un article"
        context["meta_description"] = (
            "Créez un nouvel article sur le blog."
        )
        context["is_new"] = True
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object()
        if obj.has_draft:
            initial["title"] = obj.draft_title
            initial["content"] = obj.draft_content
        return initial

    def get_success_url(self):
        return reverse("post_update", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Modifier l'article"
        context["meta_description"] = (
            "Modifiez votre article sur le blog."
        )
        context["is_new"] = False
        context["post"] = self.object
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
        qs = Post.objects.select_related("author__profile").prefetch_related(
            "comments__author__profile"
        )
        if self.request.user.is_authenticated:
            from django.db.models import Q

            return qs.filter(
                Q(status=Post.STATUS_PUBLISHED)
                | Q(author=self.request.user)
            )
        return qs.filter(status=Post.STATUS_PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        is_author = self.request.user == post.author
        viewing_draft = (
            is_author
            and self.request.GET.get("version") == "draft"
            and post.has_draft
        )

        if viewing_draft:
            context["display_title"] = post.draft_title
            context["display_content"] = post.draft_content
            context["viewing_version"] = "draft"
        else:
            context["display_title"] = post.title
            context["display_content"] = post.content
            context["viewing_version"] = "published"

        context["title"] = context["display_title"] or post.draft_title
        context["meta_description"] = (context["display_content"] or "")[:160]
        context["is_author"] = is_author
        context["approved_comments"] = (
            post.comments.filter(is_approved=True)
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


class MyPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(author=self.request.user)
            .select_related("author__profile")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Mes articles"
        context["meta_description"] = "Gérez vos articles."
        return context
