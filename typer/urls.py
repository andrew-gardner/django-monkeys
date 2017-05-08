from django.conf.urls import url

from .views import IndexView

app_name = 'typer'
urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^(?P<dieName>[a-zA-Z]+)/$', IndexView, name='index'),
]
