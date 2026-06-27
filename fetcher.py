"""
Concurrent vs Sequential API Fetcher
--------------------------------------
Fetches public weather data for multiple cities, once sequentially and once
using a thread pool, and reports the measured speedup.

Why threads work here: each request spends almost all its time *waiting* on
the network (I/O-bound), not doing CPU work. While one thread is waiting for
a response, Python's GIL lets another thread run. That's why I/O-bound tasks
like this benefit hugely from threading even though CPU-bound tasks often
don't (the GIL serializes pure-Python CPU work).

Usage:
    python fetcher.py
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Open-Meteo requires no API key, which keeps this runnable by anyone.
CITIES = {
    "Hyderabad":   (17.385, 78.4867),
    "Bengaluru":   (12.9716, 77.5946),
    "Mumbai":      (19.076, 72.8777),
    "Delhi":       (28.7041, 77.1025),
    "Chennai":     (13.0827, 80.2707),
    "Pune":        (18.5204, 73.8567),
    "Kolkata":     (22.5726, 88.3639),
    "Hyderabad2":  (17.387, 78.491),   # duplicate-ish point, fine for demo
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
    """Fetch current temperature for one city. Returns (name, temp_or_None, error_or_None)."""
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    try:
        resp = requests.get(URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        temp = data["current_weather"]["temperature"]
        return name, temp, None
    except Exception as exc:
        # A single city failing should never crash the whole batch.
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


def print_results(label, results, elapsed):
    print(f"\n--- {label} ({elapsed:.2f}s) ---")
    for name, temp, error in sorted(results, key=lambda r: r[0]):
        if error:
            print(f"  {name:12s} FAILED: {error}")
        else:
            print(f"  {name:12s} {temp}°C")


def main():
    print(f"Fetching live weather for {len(CITIES)} cities...")
    print(f"Active thread at start: {threading.current_thread().name}")

    seq_results, seq_time = run_sequential(CITIES)
    print_results("Sequential", seq_results, seq_time)

    thr_results, thr_time = run_threaded(CITIES, max_workers=10)
    print_results("Threaded (10 workers)", thr_results, thr_time)

    speedup = seq_time / thr_time if thr_time > 0 else float("inf")
    print(f"\n=== Summary ===")
    print(f"Sequential time : {seq_time:.2f}s")
    print(f"Threaded time   : {thr_time:.2f}s")
    print(f"Speedup         : {speedup:.2f}x")


if __name__ == "__main__":
    main()
