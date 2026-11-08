from django.http import JsonResponse
from django.shortcuts import render
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlencode

from django.core.exceptions import ImproperlyConfigured


def _fetch_weather(city):
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not api_key:
        raise ImproperlyConfigured('Set the OPENWEATHER_API_KEY environment variable.')

    params = urlencode({
        'q': city,
        'appid': api_key,
    })
    url = f'https://api.openweathermap.org/data/2.5/weather?{params}'
    with urllib.request.urlopen(url, timeout=10) as response:
        json_data = json.loads(response.read())

    return {
        "country_code": str(json_data['sys']['country']),
        "coordinate": str(json_data['coord']['lon']) + ', ' + str(json_data['coord']['lat']),
        "temp": str(json_data['main']['temp']) + 'k',
        "pressure": str(json_data['main']['pressure']),
        "humidity": str(json_data['main']['humidity']),
        "main": str(json_data['weather'][0]['main']),
        "description": str(json_data['weather'][0]['description']),
        "icon": str(json_data['weather'][0]['icon']),
    }


def index(request):
    data = {}
    error = None
    city = request.POST.get('city', '').strip()

    if request.method == 'POST':
        if not city:
            error = 'Please enter a city to search.'
        else:
            try:
                data = _fetch_weather(city)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    error = 'We could not find weather for that place.'
                else:
                    raise

    return render(request, 'index.html', {
        'data': data,
        'city': city,
        'error': error,
    })


def weather_data(request):
    city = request.GET.get('city', '').strip()
    if not city:
        return JsonResponse({'error': 'A city is required.'}, status=400)

    try:
        data = _fetch_weather(city)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return JsonResponse({'error': 'Place not found.'}, status=404)
        return JsonResponse({'error': 'Weather service is unavailable.'}, status=502)
    except urllib.error.URLError:
        return JsonResponse({'error': 'Weather service is unavailable.'}, status=502)

    data['city'] = city
    return JsonResponse(data)