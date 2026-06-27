"""
Concurrent vs Sequential API Fetcher
--------------------------------------
Fetches public weather data for multiple cities, once sequentially and once
using a thread pool, and reports the measured speedup.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

CITIES = {
    "Hyderabad":   (17.385, 78.4867),
    "Bengaluru":   (12.9716, 77.5946),
    "Mumbai":      (19.076, 72.8777),
    "Delhi":       (28.7041, 77.1025),
    "Chennai":     (13.0827, 80.2707),
    "Pune":        (18.5204, 73.8567),
    "Kolkata":     (22.5726, 88.3639),
    "Hyderabad2":  (17.387, 78.491),
    "Ahmedabad":   (23.0225, 72.5714),
    "Jaipur":      (26.9124, 75.7873),
}

URL = "https://api.open-meteo.com/v1/forecast"


def select_cities(count):
    """Return the first `count` cities from the predefined list."""
    if count <= 0:
        return {}

    available = list(CITIES.items())
    if count >= len(available):
        return dict(available)

    return dict(available[:count])


def fetch_city_weather(name, lat, lon, timeout=10):
    """Fetch current temperature for one city."""
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    try:
        resp = requests.get(URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        temp = data["current_weather"]["temperature"]
        return name, temp, None
    except Exception as exc:
        return name, None, str(exc)


def run_sequential(cities):
    start = time.perf_counter()
    results = []
    for name, (lat, lon) in cities.items():
        results.append(fetch_city_weather(name, lat, lon))
    elapsed = time.perf_counter() - start
    return results, elapsed


def run_threaded(cities, max_workers=10):
    start = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(fetch_city_weather, name, lat, lon): name
            for name, (lat, lon) in cities.items()
        }
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - start
    return results, elapsed
