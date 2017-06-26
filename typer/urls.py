from django.conf.urls import url

from .views import indexView, dieInstructionsView, adminSummaryHomeView, adminSummaryView

app_name = 'typer'
urlpatterns = [
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/$', indexView, name='index'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/instructions/$', dieInstructionsView, name='dieInstructions'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/$', adminSummaryHomeView, name='adminSummaryHome'),
    url(r'^(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/(?P<imageId>[0-9]+)/$', adminSummaryView, name='adminSummaryView'),
]
