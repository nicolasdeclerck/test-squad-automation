from celery import shared_task


@shared_task(bind=True, max_retries=3)
def notify_new_comment(self, comment_id):
    """Send notification when a new comment is posted."""
    try:
        from apps.blog.models import Comment

        Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return
    except Exception as exc:
        self.retry(exc=exc)
