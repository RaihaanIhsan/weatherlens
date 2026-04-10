# import requests
# from weather.weather_data import WeatherData, enrich_weather
# import config


# def geocode_city(city_name: str) -> dict | None:
#     """Convert city name to lat/lon using Open-Meteo geocoding."""
#     known = config.CITIES.get(city_name)
#     if known:
#         return known

#     url = "https://geocoding-api.open-meteo.com/v1/search"
#     resp = requests.get(url, params={"name": city_name, "count": 1})
#     results = resp.json().get("results", [])
#     if not results:
#         return None

#     r = results[0]
#     return {
#         "lat":             r["latitude"],
#         "lon":             r["longitude"],
#         "country":         r.get("country_code", "XX"),
#         "rain_sensitivity": 0.5,
#     }


# def fetch_live_weather(city_name: str) -> WeatherData | None:
#     """Fetch current weather from Open-Meteo forecast API."""
#     city_info = geocode_city(city_name)
#     if not city_info:
#         print(f"  City '{city_name}' not found.")
#         return None

#     url = "https://api.open-meteo.com/v1/forecast"
#     params = {
#         "latitude":  city_info["lat"],
#         "longitude": city_info["lon"],
#         "current":   "temperature_2m,precipitation,windspeed_10m,visibility,relativehumidity_2m",
#         "timezone":  "auto",
#     }

#     resp = requests.get(url, params=params)
#     current = resp.json().get("current", {})

#     data = WeatherData(
#         city        = city_name,
#         country     = city_info["country"],
#         temperature = current.get("temperature_2m", 0),
#         rainfall    = current.get("precipitation", 0),
#         windspeed   = current.get("windspeed_10m", 0),
#         visibility  = current.get("visibility", 10000),
#         humidity    = current.get("relativehumidity_2m", 50),
#     )

#     return enrich_weather(data)

import requests
from typing import Optional
from weather.weather_data import WeatherData, enrich_weather
import config


def geocode_city(city_name: str) -> Optional[dict]:
    known = config.CITIES.get(city_name)
    if known:
        return known

    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city_name, "count": 1})
    results = resp.json().get("results", [])
    if not results:
        return None

    r = results[0]
    return {
        "lat":              r["latitude"],
        "lon":              r["longitude"],
        "country":          r.get("country_code", "XX"),
        "rain_sensitivity": 0.5,
    }


def fetch_live_weather(city_name: str) -> Optional[WeatherData]:
    city_info = geocode_city(city_name)
    if not city_info:
        print(f"  City '{city_name}' not found.")
        return None

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  city_info["lat"],
        "longitude": city_info["lon"],
        "current":   "temperature_2m,precipitation,windspeed_10m,visibility,relativehumidity_2m",
        "timezone":  "auto",
    }

    resp = requests.get(url, params=params)
    current = resp.json().get("current", {})

    data = WeatherData(
        city        = city_name,
        country     = city_info["country"],
        temperature = current.get("temperature_2m", 0),
        rainfall    = current.get("precipitation", 0),
        windspeed   = current.get("windspeed_10m", 0),
        visibility  = current.get("visibility", 10000),
        humidity    = current.get("relativehumidity_2m", 50),
    )

    return enrich_weather(data)