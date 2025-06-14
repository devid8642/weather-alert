from django.contrib import admin

from .models import Alert, AlertConfig

admin.site.register(Alert)
admin.site.register(AlertConfig)
