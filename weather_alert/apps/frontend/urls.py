from django.urls import path
from .views import index, locations, alerts, alert_configs

urlpatterns = [
    path('', index, name='index'),
    path('locations/', locations, name='locations'),
    path('alerts/', alerts, name='alerts'),
    path('alert-configs/', alert_configs, name='alert_configs'),
]
