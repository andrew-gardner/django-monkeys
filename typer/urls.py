from django.conf.urls import url

from .views import indexView, summaryHomeView, summaryView

app_name = 'typer'
urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/$', indexView, name='index'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/summary/$', summaryHomeView, name='summaryHome'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/summary/(?P<imageId>[0-9]+)/$', summaryView, name='summaryView'),
]
