from django.urls import re_path

from .views import indexView, dieInstructionsView, adminSummaryHomeView, adminSummaryView, dieSpecificUserStatisticsView, adminStatisticsView

app_name = 'typer'
urlpatterns = [
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/$', indexView, name='index'),
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/statistics/(?P<userName>[a-zA-Z0-9\._@\-]+)/$', dieSpecificUserStatisticsView, name='dieSpecificUserStatistics'),
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/instructions/$', dieInstructionsView, name='dieInstructions'),
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/adminStatistics/$', adminStatisticsView, name='adminStatistics'),
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/$', adminSummaryHomeView, name='adminSummaryHome'),
    re_path(r'^(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/(?P<imageId>[0-9]+)/$', adminSummaryView, name='adminSummaryView'),
]
