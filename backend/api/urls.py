"""
URL patterns for the Process Monitoring API.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('processes/', views.ProcessDataView.as_view(), name='process-data'),
    path('processes/get/', views.get_processes, name='get-processes'),
    path('hosts/', views.get_hosts, name='get-hosts'),
    path('hosts/<str:hostname>/processes/', views.get_host_processes, name='host-processes'),
    path('clear-old-data/', views.clear_old_data, name='clear-old-data'),
] 