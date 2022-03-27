    # Создать двух пользователей (с помощью метода User.objects.create_user('username')).
from news.models import *
from django.contrib.auth.models import User

user1 = User.objects.create_user('news_admin', password='123')
user1.is_superuser=True
user1.is_staff=True
user1.save()

user2 = User.objects.create_user('reader', password='qwe')


    # Создать два объекта модели Author, связанные с пользователями.
a1 = Author.objects.create(user_id=user1)
a2 = Author.objects.create(user_id=user2)


    # Добавить 4 категории в модель Category.
Category.objects.create(name='python')
Category.objects.create(name='программирование')
Category.objects.create(name='юмор')
Category.objects.create(name='новые технологии')

    # Добавить 2 статьи и 1 новость.
Post.objects.create(header='Суперкомпьтер помогает разрабатывать алгоритмы для проектирования нейросетей, которые будут обнаруживать рак', types='NS', text='Суперкомпьютер Summit Ок-Риджской национальной лаборатории (ORNL), самый быстрый в мире, используется для разработки алгоритмов, которые могут помочь исследователям автоматически проектировать нейронные сети для исследований рака. Это позволит врачам быстрее распознавать характер опухолей.', author_id=a1)
Post.objects.create(header='Айтишники-мужчины, будьте осторожны!', types='AR', text='ПЕРЕУСТАНОВИ МНЕ ВИНДУ - пост сдал, УСТАНОВИ МНЕ VPN - пост принял.', author_id=a2)
Post.objects.create(header='А что с хостингом?', types='AR', text='В свете последних двух недель IT-сфера в России претерпевает серьезные изменения: уход IT-гигантов с российского рынка, приостановка поставок и так далее, далее, далее… Первое, что хочется сделать — взять и заплакать. Второе — успокоиться, попытаться хоть как-то проанализировать ситуацию и понять, чего ожидать. Это далеко не первая статья на хабре, пытающаяся дать некий прогноз, да и явно не последняя. В рамках неё мы попытаемся определить, что ждет рынок хостинга в России и поразмышляем, как это скажется на клиентах.', author_id=a1)

    # Присвоить им категории (как минимум в одной статье/новости должно быть не меньше 2 категорий).
n1 = Post.objects.get(id=1)
c1 = Category.objects.get(name='новые технологии')
c2 = Category.objects.get(name='программирование')
PostCategory.objects.create(post_id=n1, category_id=c1)
PostCategory.objects.create(post_id=Post.objects.get(id=2), category_id=Category.objects.get(name='юмор'))
PostCategory.objects.create(post_id=Post.objects.get(id=3), category_id=c2)
PostCategory.objects.create(post_id=Post.objects.get(id=3), category_id=Category.objects.get(name='python'))

    # Создать как минимум 4 комментария к разным объектам модели Post (в каждом объекте должен быть как минимум один комментарий).
Comment.objects.create(text='Это здорово!', post_id=n1, user_id=user1)
Comment.objects.create(text='Согласен', post_id=n1, user_id=user2)
Comment.objects.create(text='))))))))))))))))))))))', post_id=Post.objects.get(id=2), user_id=user1)
Comment.objects.create(text='Все это как-то неправильно...', post_id=Post.objects.get(id=3), user_id=user1)

    # Применяя функции like() и dislike() к статьям/новостям и комментариям, скорректировать рейтинги этих объектов.
    # публикации
n1.like()
n1.like()
n1.like()
Post.objects.get(id=2).dislike()
Post.objects.get(id=3).dislike()
Post.objects.get(id=3).like()
Post.objects.get(id=3).like()
    # комментарии
Comment.objects.get(id=1).dislike()
Comment.objects.get(id=2).like()
Comment.objects.get(id=3).like()
Comment.objects.get(id=4).dislike()


    # Обновить рейтинги пользователей.
a1.update_rating()
a2.update_rating()


    # Вывести username и рейтинг лучшего пользователя (применяя сортировку и возвращая поля первого объекта).
print(Author.objects.all().order_by('-rating').values('user_id__username', 'rating')[0])
# или так
print(f"Лучший пользователь: {Author.objects.all().order_by('-rating')[0].user_id.username} c рейтингом {Author.objects.all().order_by('-rating')[0].rating}")

    # Вывести дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи, основываясь на лайках/дислайках к этой статье.
Post.objects.all().order_by('-rating').values('date_create', 'author_id__user_id__username', 'rating', 'header')[0]
Post.objects.all().order_by('-rating')[0].preview()
# или
best_post = Post.objects.all().order_by('-rating')[0]
print(f'Дата добавления: {best_post.date_create}')
print(f'Автор публикации: {best_post.author_id.user_id.username}')
print(f'Рейтинг публикации: {best_post.rating}')
print(f'Заголовок публикации: {best_post.header}')
print(f'Превью публикации: {best_post.preview()}')


    # Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье.
Comment.objects.filter(post_id=Post.objects.all().order_by('-rating')[0]).values('date_create', 'user_id__username', 'rating', 'text')
# или
comment_list = Comment.objects.filter(post_id=best_post)
for c in comment_list:
    print(f'Дата добавления комментария: {c.date_create}')
    print(f'Пользователь: {c.user_id.username}')
    print(f'Рейтинг комментария: {c.rating}')
    print(f'Комментарий: {c.text}')