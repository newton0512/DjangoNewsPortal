from django.contrib.sites.models import Site
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import *


@receiver(m2m_changed, sender=Post.categories.through)
def send_mail_on_create_post(sender, action, instance, **kwargs):
    # отправляем письмо
    if action == 'post_add':
        user_list = []
        cats = instance.categories.all()
        domain = Site.objects.get_current().domain
        for c in cats:
            users = c.subscribers.all()
            for u in users:
                path = instance.get_absolute_url()
                html_content = render_to_string(
                    'mail/new_post.html',
                    {
                        'username': u.username,
                        'message': instance.text[:50] + '...',
                        'post_url': f'http://{domain}{path}',
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'{instance.header}',
                    body=instance.text[:50] + '...',
                    from_email='max.shatkevich@yandex.ru',
                    to=[u.email],  # это то же, что и recipients_list
                )
            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()  # отсылаем

        #send_mail(
        #    subject=f'{instance.header}',
        #    message=instance.text[:50] + '...',
        #    from_email='max.shatkevich@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        #    recipient_list=list(set(user_list))  # здесь список получателей.
        #)
