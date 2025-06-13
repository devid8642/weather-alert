from ninja import NinjaAPI

from apps.alerts.views import alert_config_router, alert_router
from apps.location.views import location_router
from apps.temperature.views import temperature_router

api = NinjaAPI(title='Weather Alert API', version='1.0.0')

api.add_router('/locations/', location_router)
api.add_router('/alert-configs/', alert_config_router)
api.add_router('/alerts/', alert_router)
api.add_router('/temperature-logs/', temperature_router)
