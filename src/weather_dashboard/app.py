import pandas as pd
import streamlit as st

from src.weather_dashboard.fetcher import CITIES, run_sequential, run_threaded, select_cities


st.set_page_config(page_title="Weather Fetcher Dashboard", page_icon="🌦️", layout="wide")

st.title("Weather Fetcher Performance Dashboard")
st.caption("Compare sequential and threaded weather retrieval across a configurable set of cities.")

with st.sidebar:
    st.header("Run configuration")
    city_count = st.slider("Number of cities", min_value=1, max_value=len(CITIES), value=min(6, len(CITIES)))
    thread_count = st.slider("Thread count", min_value=1, max_value=12, value=4)
    run_button = st.button("Run benchmark", type="primary")

if run_button:
    selected_cities = select_cities(city_count)
    if not selected_cities:
        st.error("Please choose at least one city.")
        st.stop()

    seq_results, seq_time = run_sequential(selected_cities)
    thr_results, thr_time = run_threaded(selected_cities, max_workers=thread_count)

    speedup = seq_time / thr_time if thr_time > 0 else float("inf")

    summary_df = pd.DataFrame(
        [
            {"Mode": "Sequential", "Execution time (s)": round(seq_time, 3)},
            {"Mode": "Concurrent", "Execution time (s)": round(thr_time, 3)},
        ]
    )

    st.subheader("Benchmark summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Cities", city_count)
    col2.metric("Thread count", thread_count)
    col3.metric("Speedup", f"{speedup:.2f}x")

    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Fetched weather")
    results = []
    for name, temp, error in sorted(seq_results, key=lambda item: item[0]):
        results.append({"City": name, "Sequential temp (°C)": temp if temp is not None else "—", "Sequential error": error or ""})

    threaded_lookup = {name: temp for name, temp, _ in thr_results}
    for item in results:
        city = item["City"]
        item["Concurrent temp (°C)"] = threaded_lookup.get(city, None) if threaded_lookup.get(city) is not None else "—"

    weather_df = pd.DataFrame(results)
    st.dataframe(weather_df, use_container_width=True, hide_index=True)

    st.subheader("Execution time comparison")
    chart_df = pd.DataFrame(
        {
            "Mode": ["Sequential", "Concurrent"],
            "Execution time (s)": [seq_time, thr_time],
        }
    )
    st.bar_chart(chart_df, x="Mode", y="Execution time (s)")
else:
    st.info("Select your inputs and press Run benchmark to begin.")
