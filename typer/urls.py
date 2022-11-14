from django.urls import path

from .views import indexView, dieInstructionsView, adminSummaryHomeView, adminSummaryView, dieSpecificUserStatisticsView, adminStatisticsView

app_name = 'typer'
urlpatterns = [
    path('<str:dieName>/', indexView, name='index'),
    path('<str:dieName>/statistics/<str:userName>/', dieSpecificUserStatisticsView, name='dieSpecificUserStatistics'),
    path('<str:dieName>/instructions/', dieInstructionsView, name='dieInstructions'),
    path('<str:dieName>/adminStatistics/', adminStatisticsView, name='adminStatistics'),
    path('<str:dieName>/adminSummary/', adminSummaryHomeView, name='adminSummaryHome'),
    path('<str:dieName>/adminSummary/<int:imageId>/', adminSummaryView, name='adminSummaryView'),
]
