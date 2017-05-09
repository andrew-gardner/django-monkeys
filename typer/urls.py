from django.conf.urls import url

from .views import indexView, summaryHomeView, summaryView

app_name = 'typer'
urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^(?P<dieName>[a-zA-Z]+)/$', indexView, name='index'),
    url(r'^(?P<dieName>[a-zA-Z]+)/summary/$', summaryHomeView, name='summaryHome'),
    url(r'^(?P<dieName>[a-zA-Z]+)/summary/(?P<imageId>[0-9]+)/$', summaryView, name='summaryView'),
]
