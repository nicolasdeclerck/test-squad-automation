from django.contrib import admin

from .models import Comment, Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "created_at")
    list_filter = ("status", "tags")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.action(description="Approuver les commentaires sélectionnés")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "is_approved")
    list_filter = ("is_approved", "created_at")
    actions = [approve_comments]
