from django.urls import path
from . import views

urlpatterns = [
    # 1. The Homepage (Where users type the title)
    path('', views.title_checker, name='index'),

    # 2. The Result Page (Where users see the report)
    # Even if your view is named 'title_checker', the URL can be 'result/'
    path('result/', views.title_checker, name='result'),
]