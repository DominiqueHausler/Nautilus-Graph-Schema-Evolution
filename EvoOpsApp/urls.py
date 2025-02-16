from django.urls import path
from . import views

app_name = 'EvoOpsApp'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('documentation/', views.documentation, name='documentation'),
    path('nautilus/', views.nautilus, name='nautilus'),
    path('download_history/', views.download_history, name='download_history'),
    path('delete_history/', views.delete_history, name='delete_history'),

]
