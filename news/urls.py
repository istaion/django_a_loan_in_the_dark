from django.urls import path
from news.views import get_all_news, news_detail, create_news, update_news, news_by_user, delete_news

app_name = 'news'

urlpatterns = [
    path("", get_all_news, name="all_news"),
    path("me/", news_by_user, name="my_news"),
    path("add/", create_news, name="create_news"),
    path("<int:id>/", news_detail, name="news_detail"),
    path("edit/<int:id>/", update_news, name="updated_news"),
    path("delete/<int:id>/", delete_news, name="delete_news")
]