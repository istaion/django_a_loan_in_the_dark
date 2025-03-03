from django.shortcuts import render
from news.models import New
from django.views import View
from news.forms import NewsForm, EditNewsForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

import datetime

app_name = 'news' 

# Create your views here.
@login_required
def get_all_news(request):
    news_list = New.objects.all()
    return render(request,"news/news_listing.html", context={"news_list": news_list})

@login_required
def news_detail(request, id):
    news = New.objects.get(id=id)
    return render(request,"news/news_detail.html", context={"news": news})

@login_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            current_news = form.save(commit=False)
            current_news.author = request.user
            current_news.save()

            return redirect('news:all_news')
    else:
        form = NewsForm()
    return render(request, "news/create_news_form.html", {"form": form})

@login_required
def update_news(request, id):
    updated_news = New.objects.get(id=id)

    if request.method == 'POST':
        form = EditNewsForm(request.POST, request.FILES, instance=updated_news)
        if form.is_valid():
            form.save()

            return redirect('news:all_news')
    
    else:
        form = EditNewsForm(instance=updated_news)

    return render(request, 'news/news_update.html', {'form': form, 'updated_news': updated_news})

@login_required
def news_by_user(request):
    my_news = New.objects.filter(author=request.user)
    return render(request, "news/all_my_news.html", {"my_news": my_news})

@login_required
def delete_news(request, id):
    news = New.objects.get(id=id)

    if request.method == "POST":
        news.delete()
        return redirect("news:my_news")

    return render(request, "news/news_delete.html", {"news": news})