import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from datetime import datetime, timedelta

from ...models import *

logger = logging.getLogger(__name__)


def my_job():
    #  Your job processing logic here...
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
                    from_email='max.shatkevich@yandex.ru',
                    to=[u.email],  # это то же, что и recipients_list
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html
                msg.send()  # отсылаем


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            # trigger=CronTrigger(minute="*/1"),  # для тестирования
            trigger=CronTrigger(day_of_week="sun", hour="00", minute="00"),
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")