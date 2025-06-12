from ninja import NinjaAPI

from apps.location.views import location_router

api = NinjaAPI(title='Weather Alert API', version='1.0.0')

api.add_router('/locations/', location_router)
