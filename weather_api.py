"""
weather_api.py
--------------
Thin wrapper around the Open-Meteo public API (https://open-meteo.com).

Open-Meteo is free and needs NO API key, so there are no secrets in this repo.
Two endpoints are used:

  1. Geocoding: turn a city name into latitude/longitude.
     https://geocoding-api.open-meteo.com/v1/search
  2. Forecast:  get the current weather for a lat/lon.
     https://api.open-meteo.com/v1/forecast

Everything the game needs to talk to the network lives here, so the game file
(weather_quiz.py) never has to think about HTTP, JSON, or error types beyond a
single custom exception: WeatherError.
"""

import requests

# Base URLs for the two Open-Meteo endpoints we use.
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# How long (seconds) we wait on any single request before giving up. Keeps the
# game from hanging forever if the network is flaky.
TIMEOUT = 10


class WeatherError(Exception):
    """Raised for any problem reaching or reading the weather API.

    The game catches this one type and prints a friendly message, so a dropped
    wifi connection or an odd response never crashes the program with a
    traceback.
    """


# WMO weather interpretation codes -> human-readable text.
# Open-Meteo returns weather as an integer "weather_code" following the WMO
# standard. This maps each code to something a person can read.
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def describe_code(code):
    """Return readable text for a WMO weather code (fallback if unknown)."""
    return WMO_CODES.get(code, "Unknown conditions")


def c_to_f(temp_c):
    """Convert Celsius to Fahrenheit."""
    return temp_c * 9 / 5 + 32


def _get_json(url, params):
    """Do a GET request and return parsed JSON, or raise WeatherError.

    This is the single choke point for network access. Every failure mode a
    real network throws at us -- no wifi, DNS failure, timeout, a 500 from the
    server, or a body that isn't valid JSON -- is converted into one
    WeatherError so callers only have to handle one thing.
    """
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()          # turn 4xx/5xx into an exception
        return resp.json()               # may raise ValueError on bad JSON
    except requests.exceptions.Timeout:
        raise WeatherError("The weather service took too long to respond (timed out).")
    except requests.exceptions.ConnectionError:
        raise WeatherError("Couldn't reach the weather service -- check your internet connection.")
    except requests.exceptions.HTTPError as exc:
        raise WeatherError(f"The weather service returned an error ({exc.response.status_code}).")
    except requests.exceptions.RequestException as exc:
        # Any other requests-level failure.
        raise WeatherError(f"Network problem talking to the weather service: {exc}")
    except ValueError as exc:
        # resp.json() failed -- the server sent something that wasn't JSON.
        raise WeatherError(f"Got an unreadable response from the weather service: {exc}")


def geocode_city(name):
    """Look up a city by name.

    Returns a dict {name, country, lat, lon} for the best match, or None if no
    city matched (e.g. a misspelling). Raises WeatherError on a network problem.
    """
    params = {"name": name, "count": 1, "language": "en", "format": "json"}
    data = _get_json(GEOCODE_URL, params)

    results = data.get("results")
    if not results:
        # No "results" key, or an empty list -> the city wasn't found.
        return None

    top = results[0]
    return {
        "name": top.get("name", name),
        "country": top.get("country", ""),
        "lat": top["latitude"],
        "lon": top["longitude"],
    }


def get_current_weather(lat, lon):
    """Fetch current weather for a coordinate.

    Returns a normalized dict:
        {temp_c, feels_c, humidity, wind_kmh, code, description}
    Raises WeatherError on a network problem OR if the response is missing the
    fields we expect (a malformed / unexpected payload).
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,"
                   "wind_speed_10m,apparent_temperature",
    }
    data = _get_json(FORECAST_URL, params)

    current = data.get("current")
    if not current:
        raise WeatherError("Weather response was missing the 'current' data block.")

    try:
        code = current["weather_code"]
        return {
            "temp_c": current["temperature_2m"],
            "feels_c": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_kmh": current["wind_speed_10m"],
            "code": code,
            "description": describe_code(code),
        }
    except KeyError as exc:
        # A field we rely on wasn't present -- treat as a bad payload.
        raise WeatherError(f"Weather response was missing an expected field: {exc}")
