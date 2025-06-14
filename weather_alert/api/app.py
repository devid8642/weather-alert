from ninja import NinjaAPI

from weather_alert.apps.alerts.views import alert_config_router, alert_router
from weather_alert.apps.location.views import location_router
from weather_alert.apps.temperature.views import temperature_router

api = NinjaAPI(title='Weather Alert API', version='1.0.0')

api.add_router('/locations/', location_router)
api.add_router('/alert-configs/', alert_config_router)
api.add_router('/alerts/', alert_router)
api.add_router('/temperature-logs/', temperature_router)
