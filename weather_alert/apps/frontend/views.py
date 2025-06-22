from django.shortcuts import render


async def index(request):
    return render(request, 'index.html')


async def locations(request):
    return render(request, 'locations.html')


async def alerts(request):
    return render(request, 'alerts.html')

async def alert_configs(request):
    return render(request, 'alert_configs.html')
