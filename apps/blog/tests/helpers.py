API_POSTS_URL = "/api/blog/posts/"


def api_post_url(slug):
    return f"/api/blog/posts/{slug}/"


def api_autosave_url(slug):
    return f"/api/blog/posts/{slug}/autosave/"


def api_publish_url(slug):
    return f"/api/blog/posts/{slug}/publish/"


def api_comments_url(slug):
    return f"/api/blog/posts/{slug}/comments/"


def api_comment_delete_url(pk):
    return f"/api/blog/comments/{pk}/"


def api_versions_url(slug):
    return f"/api/blog/posts/{slug}/versions/"


def api_version_detail_url(slug, version_number):
    return f"/api/blog/posts/{slug}/versions/{version_number}/"


def api_version_restore_url(slug, version_number):
    return f"/api/blog/posts/{slug}/versions/{version_number}/restore/"


API_TAGS_URL = "/api/blog/tags/"

API_UPLOAD_IMAGE_URL = "/api/blog/upload-image/"
