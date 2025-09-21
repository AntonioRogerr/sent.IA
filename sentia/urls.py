from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('delete_session/<int:session_id>/', views.delete_session_view, name='delete_session'),
    path('export/csv/', views.export_filtered_data_view, name='export_filtered_data_csv'),
    path('export/json/', views.export_filtered_data_json_view, name='export_filtered_data_json'),
]