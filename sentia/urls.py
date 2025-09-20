from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # --- NOVA LINHA ADICIONADA AQUI ---
    path('delete_session/<int:session_id>/', views.delete_session_view, name='delete_session'),
]