from django.contrib import admin
from django.urls import path, include
from . import views



urlpatterns = [
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard')
#    path('blog/', views.blog) na primeira parte colocamos o nome da rota que aparece no site, na segunda puxamos a view 
]
