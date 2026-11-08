import json
import urllib.error
from io import BytesIO
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


@patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'test-key'})
class WeatherViewTests(TestCase):
    @patch(
        'weather.views.urllib.request.urlopen',
        side_effect=urllib.error.HTTPError(
            'https://api.openweathermap.org/data/2.5/weather',
            404,
            'Not Found',
            None,
            None,
        ),
    )
    def test_unknown_city_shows_not_found_message(self, _urlopen):
        response = self.client.post(reverse('index'), {'city': 'Nowhere'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Page Not Found')
        self.assertContains(response, 'Nowhere')
        self.assertContains(response, 'Try another search')

    @patch('weather.views.urllib.request.urlopen')
    def test_weather_result_displays_weather_icon(self, urlopen):
        payload = {
            'sys': {'country': 'GB'},
            'coord': {'lon': -0.12, 'lat': 51.51},
            'main': {'temp': 280, 'pressure': 1012, 'humidity': 70},
            'weather': [{
                'main': 'Clouds',
                'description': 'scattered clouds',
                'icon': '03d',
            }],
        }
        urlopen.return_value = BytesIO(json.dumps(payload).encode())

        response = self.client.post(reverse('index'), {'city': 'London'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'https://openweathermap.org/img/wn/03d@2x.png',
        )
        self.assertContains(response, 'London')
        self.assertContains(response, 'scattered clouds')

    @patch('weather.views.urllib.request.urlopen')
    def test_weather_data_endpoint_returns_weather_for_saved_city(self, urlopen):
        payload = {
            'sys': {'country': 'GB'},
            'coord': {'lon': -0.12, 'lat': 51.51},
            'main': {'temp': 280, 'pressure': 1012, 'humidity': 70},
            'weather': [{
                'main': 'Clouds',
                'description': 'scattered clouds',
                'icon': '03d',
            }],
        }
        urlopen.return_value = BytesIO(json.dumps(payload).encode())

        response = self.client.get(
            reverse('weather_data'),
            {'city': 'London'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['city'], 'London')
        self.assertEqual(response.json()['icon'], '03d')
        self.assertEqual(response.json()['humidity'], '70')

    @patch(
        'weather.views.urllib.request.urlopen',
        side_effect=urllib.error.HTTPError(
            'https://api.openweathermap.org/data/2.5/weather',
            404,
            'Not Found',
            None,
            None,
        ),
    )
    def test_weather_data_endpoint_reports_unknown_city(self, _urlopen):
        response = self.client.get(
            reverse('weather_data'),
            {'city': 'Nowhere'},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Place not found.')
