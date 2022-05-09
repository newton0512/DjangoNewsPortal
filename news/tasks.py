from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings
from datetime import datetime, timedelta

from .models import *


@shared_task
def task_send_mail_on_create_post(post_id, user_id):
    domain = Site.objects.get_current().domain
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=user_id)
    path = post.get_absolute_url()
    html_content = render_to_string(
        'mail/new_post.html',
        {
            'username': user.username,
            'message': post.text[:50] + '...',
            'post_url': f'http://{domain}{path}',
        }
    )
    msg = EmailMultiAlternatives(
        subject=f'{post.header}',
        body=post.text[:50] + '...',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],  # это то же, что и recipients_list
    )
    msg.attach_alternative(html_content, "text/html")  # добавляем html
    msg.send()  # отсылаем

@shared_task
def task_send_week_news():
    one_week_ago = datetime.today() - timedelta(days=7)
    cats = Category.objects.all()
    domain = Site.objects.get_current().domain
    for c in cats:
        posts = Post.objects.filter(date_create__gte=one_week_ago, categories=c)
        users = c.subscribers.all()
        if posts.count() > 0:
            for u in users:
                path = c.get_absolute_url()
                html_content = render_to_string(
                    'mail/week_post.html',
                    {
                        'username': u.username,
                        'category_name': c.name,
                        'cat_url': f'http://{domain}{path}',
                        'posts': posts,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'Последние публикации - {c.name}',
                    body=f'Высылаем вам подборку последних публикаций из категории "{c.name}".',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[u.email],  # это то же, что и recipients_list
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html
                msg.send()  # отсылаем
