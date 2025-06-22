from django.conf import settings


def api_base_url(request):
    """
    Variável de contexto que é exposta para todos os templates da aplicação
    """
    return {
        'API_BASE_URL': settings.API_BASE_URL
    }
