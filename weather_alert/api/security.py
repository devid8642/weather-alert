from django.conf import settings
from ninja.security import APIKeyHeader


class N8NApiKey(APIKeyHeader):
    param_name = 'N8N_WEBHOOK_KEY'

    def authenticate(self, request, key):
        if key == settings.N8N_WEBHOOK_HEADER_KEY:
            return key


n8n_header_key = N8NApiKey()
