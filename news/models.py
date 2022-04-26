from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse

news = 'NS'
article = 'AR'

POST_TYPES = [
    (news, 'Новость'),
    (article, 'Статья'),
]


class Author(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)  # связь с классом User из Django
    rating = models.IntegerField(default=0)  # рейтинг автора

    def update_rating(self):    # обновление рейтинга автора
        rating_post = Post.objects.filter(author_id=self.pk).aggregate(Sum('rating'))['rating__sum'] * 3
        rating_comment = Comment.objects.filter(user_id=self.user_id).aggregate(Sum('rating'))['rating__sum']
        rating_all_comment = Comment.objects.filter(post_id__author_id=self.pk).aggregate(Sum('rating'))['rating__sum']
        self.rating = rating_post + rating_comment + rating_all_comment
        self.save()

    def __str__(self):
        return self.user_id.username


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # название категории, уникальное поле
    subscribers = models.ManyToManyField(User, through='SubscribersCategory')  # категории публикаций

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_id': self.pk})


class Post(models.Model):
    types = models.CharField(max_length=2, choices=POST_TYPES, default=news)  # тип публикации: новость или статья
    date_create = models.DateTimeField(auto_now_add=True)  # дата и время создания публикации
    header = models.CharField(max_length=255)  # заголовок публикации
    text = models.TextField()  # текст публикации
    rating = models.IntegerField(default=0)  # рейтинг публикации
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)  # автор публикации
    categories = models.ManyToManyField(Category, through='PostCategory')  # категории публикаций

    def like(self):  # увеличение рейтинга публикации
        self.rating += 1
        self.save()

    def dislike(self):  # уменьшение рейтинга публикации
        self.rating -= 1
        self.save()

    def preview(self):  # предварительный просмотр публикации
        return self.text[:124] + '...'

    def __str__(self):
        return self.header

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])


class PostCategory(models.Model):   # промежуточная таблица для связи много-к-многим
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)     # ид публикации
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)     # ид категории


class Comment(models.Model):
    text = models.TextField()  # текст комментария
    date_create = models.DateTimeField(auto_now_add=True)  # дата и время создания комментария
    rating = models.IntegerField(default=0)  # рейтинг комментария
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)  # ид публикации
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)  # ид пользователя

    def like(self):  # увеличение рейтинга комментария
        self.rating += 1
        self.save()

    def dislike(self):  # уменьшение рейтинга комментария
        self.rating -= 1
        self.save()

class SubscribersCategory(models.Model):   # промежуточная таблица для связи много-к-многим
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)     # ид пользователя
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)     # ид категории
