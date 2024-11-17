from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('check_status/<str:request_id>/', views.check_status, name='check_status'),
    path('download_output_csv/<str:request_id>/', views.download_output_csv, name='download_output_csv'),
]
