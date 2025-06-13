from ninja import NinjaAPI

from apps.location.views import location_router
from apps.alerts.views import alert_router, alert_config_router

api = NinjaAPI(title='Weather Alert API', version='1.0.0')

api.add_router('/locations/', location_router)
api.add_router("/alert-configs/", alert_config_router)
api.add_router("/alerts/", alert_router)
