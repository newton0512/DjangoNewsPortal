from django.urls import path, include
# Импортируем созданное нами представление
from .views import *

urlpatterns = [
    # path — означает путь.
    # В данном случае путь ко всем товарам у нас останется пустым,
    # чуть позже станет ясно почему.
    # Т.к. наше объявленное представление является классом,
    # а Django ожидает функцию, нам надо представить этот класс в виде view.
    # Для этого вызываем метод as_view.
    path('news/', PostList.as_view(), name='postlist'),
    path('category/<int:cat_id>/', show_category, name='category'),
    path('news/<int:pk>/', PostView.as_view(), name='news_detail'),
    path('news/search/', search_page, name='postlist_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('articles/create/', ArticleCreate.as_view(), name='art_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='articles_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='articles_delete'),
    path('user/', include('allauth.urls')),
    path('user/edit/', UserDataUpdate.as_view(), name='user_edit'),
    path('user/become_an_author/', upgrade_me, name='become_an_author'),
    path('category/<int:cat_id>/subscribe', subscribe_on_cat, name='subscribe'),
    path('category/<int:cat_id>/unsubscribe', unsubscribe_cat, name='unsubscribe'),
    path('accounts/', include('allauth.urls')),
]
