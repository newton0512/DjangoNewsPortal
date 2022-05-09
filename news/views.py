from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, POST_TYPES
from .filters import *
from .forms import *
from .models import POST_TYPES, news as st_news, article as st_article
from .tasks import *


paginator_items_count = 10


class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-date_create'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news/postlist.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = paginator_items_count

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        context['cats'] = Category.objects.all()
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class PostView(DetailView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news/post.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat'] = dict(POST_TYPES)[self.object.types]
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['cats'] = Category.objects.all()
        return context


def search_page(request):
    queryset = Post.objects.all()
    filterset = NewsFilter(request.GET, queryset)
    page = request.GET.get('page')
    paginator = Paginator(filterset.qs, paginator_items_count)
    try:
        f_qs = paginator.get_page(page)
    except PageNotAnInteger:
        f_qs = paginator.get_page(paginator_items_count)
    except EmptyPage:
        f_qs = paginator.get_page(paginator.num_pages)

    context = {
        'posts': f_qs,
        'filterset': filterset,
        'page_obj': f_qs,
        'paginator': paginator,
        'cats': Category.objects.all(),
    }

    return render(request, 'news/search.html', context=context)


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.types = st_news
        author = Author.objects.get(user_id=self.request.user)
        news.author_id = author
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание новости:'
        return context


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        art = form.save(commit=False)
        art.types = st_article
        author = Author.objects.get(user_id=self.request.user)
        art.author_id = author
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание статьи:'
        return context


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование публикации:'
        return context


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('postlist')


class UserDataUpdate(LoginRequiredMixin, UpdateView):
    form_class = UserDataForm
    model = User
    template_name = 'account/user_edit.html'
    success_url = reverse_lazy('postlist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование данных пользователя:'
        return context

    def get_object(self):
        return self.request.user


def logout_user(request):
    logout(request)
    return redirect('login')

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = reverse_lazy('postlist')
    template_name = 'account/user_edit.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('postlist')


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
        Author.objects.create(user_id=user)
    return redirect('postlist')

def test_f(request):
    print('*******NENENENENENENNENEN*********')
    printer.delay(4)
    hello.delay()
    return redirect('postlist')


def show_category(request, cat_id):
    posts = Post.objects.filter(categories__id=cat_id).order_by('-date_create')
    cats = Category.objects.all()
    try:
        already_subscribed = SubscribersCategory.objects.get(user_id=request.user.pk, category_id=cat_id)
    except SubscribersCategory.DoesNotExist:
        already_subscribed = None
    context = {
        'posts': posts,
        'cats': cats,
        'current_cat': Category.objects.get(id=cat_id),
        'already_subscribed': already_subscribed,
    }

    return render(request, 'news/postlist.html', context=context)


@login_required
def subscribe_on_cat(request, cat_id):
    user = request.user
    cat = Category.objects.get(id=cat_id)
    cat.subscribers.add(user)
    return redirect('category', cat_id=cat_id)


@login_required
def unsubscribe_cat(request, cat_id):
    user = request.user
    cat = Category.objects.get(id=cat_id)
    cat.subscribers.remove(user)
    return redirect('category', cat_id=cat_id)