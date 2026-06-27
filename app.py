import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

from src.weather_dashboard.fetcher import (
    CITIES,
    run_sequential,
    run_threaded,
    select_cities,
)

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Concurrent Weather Performance Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

.main{
    background-color:#f7f9fc;
}

.hero{
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    padding:35px;
    border-radius:18px;
    color:white;
    text-align:center;
    margin-bottom:25px;
}

.hero h1{
    font-size:42px;
    margin-bottom:10px;
}

.hero p{
    font-size:18px;
}

.metric-box{
    background:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.1);
}

.footer{
    text-align:center;
    color:gray;
    font-size:14px;
    padding-top:25px;
}

hr{
    margin-top:30px;
    margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HERO ---------------- #

st.markdown("""
<div class="hero">

<h1>⚡ Concurrent Weather Fetcher & Performance Analyzer</h1>

<p>
Benchmark Sequential vs Concurrent API Requests using
<b>Python ThreadPoolExecutor</b>
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.title("⚙ Configuration")

    city_count = st.slider(
        "Number of Cities",
        min_value=1,
        max_value=len(CITIES),
        value=6,
    )

    thread_count = st.slider(
        "Thread Count",
        min_value=1,
        max_value=12,
        value=4,
    )
    run_button = st.button(
        "🚀 Run Benchmark",
        use_container_width=True,
        type="primary"
    )
    st.divider()

    st.subheader("📦 Tech Stack")

    st.markdown("""
- Python
- Streamlit
- ThreadPoolExecutor
- Requests
- Pandas
- Plotly
- Open-Meteo API
""")

    st.divider()

    st.subheader("📖 Concepts")

    st.markdown("""
✅ Multithreading

✅ Concurrency

✅ REST APIs

✅ Performance Benchmarking

✅ I/O Bound Tasks
""")

    

# ---------------- SESSION STATE ---------------- #

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TABS ---------------- #

dashboard_tab, weather_tab, history_tab, about_tab = st.tabs(
    [
        "📊 Dashboard",
        "🌦 Weather Results",
        "📜 Benchmark History",
        "📘 About Project",
    ]
)
# ---------------- RUN BENCHMARK ---------------- #

if run_button:

    selected_cities = select_cities(city_count)

    if not selected_cities:
        st.error("Please select at least one city.")
        st.stop()

    with st.spinner("Fetching live weather data..."):

        seq_results, seq_time = run_sequential(selected_cities)

        thr_results, thr_time = run_threaded(
            selected_cities,
            max_workers=thread_count
        )

    st.success("✅ Benchmark completed successfully!")

    speedup = seq_time / thr_time if thr_time > 0 else 0

    improvement = (
        ((seq_time - thr_time) / seq_time) * 100
        if seq_time > 0
        else 0
    )

    # Save benchmark history

    st.session_state.history.append(
        {
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Cities": city_count,
            "Threads": thread_count,
            "Sequential (s)": round(seq_time, 3),
            "Concurrent (s)": round(thr_time, 3),
            "Speedup": round(speedup, 2),
        }
    )

    # ================= DASHBOARD TAB ================= #

    with dashboard_tab:

        st.subheader("📊 Benchmark Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "⏱ Sequential",
            f"{seq_time:.3f}s",
        )

        col2.metric(
            "⚡ Concurrent",
            f"{thr_time:.3f}s",
        )

        col3.metric(
            "🚀 Speedup",
            f"{speedup:.2f}x",
        )

        col4.metric(
            "🏙 Cities",
            city_count,
        )

        st.divider()

        chart_df = pd.DataFrame(
            {
                "Mode": [
                    "Sequential",
                    "Concurrent",
                ],
                "Execution Time (seconds)": [
                    seq_time,
                    thr_time,
                ],
            }
        )

        fig = px.bar(
            chart_df,
            x="Mode",
            y="Execution Time (seconds)",
            color="Mode",
            text_auto=".3f",
            title="Execution Time Comparison",
        )

        fig.update_layout(
            xaxis_title="Execution Mode",
            yaxis_title="Execution Time (seconds)",
            height=450,
            showlegend=False,
        )

        left, right = st.columns([2.2, 1])

        with left:
            st.plotly_chart(
            fig,
            use_container_width=True,
        )

        with right:
            st.subheader("📈 Performance")

            st.metric(
            "Speedup",
            f"{speedup:.2f}×"
        )

            st.metric(
            "Reduction",
            f"{improvement:.1f}%"
        )

            st.metric(
            "Threads",
            thread_count
            )

            if improvement >= 70:
                st.success("Excellent improvement!")

            elif improvement >= 40:
                st.info("Good improvement!")

            else:
                st.warning("Limited improvement")

        st.markdown("### 💡 Recommendation")

        st.info(
        "ThreadPoolExecutor is ideal for I/O-bound workloads because network waiting time overlaps across threads."
        )
        
            # ================= WEATHER TAB ================= #

    with weather_tab:

        st.subheader("🌦 Live Weather Results")

        threaded_lookup = {
            name: temp
            for name, temp, _ in thr_results
        }

        rows = []

        for name, temp, error in sorted(
            seq_results,
            key=lambda x: x[0],
        ):

            rows.append(
                {
                    "City": name,
                    "Sequential Temp (°C)": (
                        temp if temp is not None else "-"
                    ),
                    "Concurrent Temp (°C)": (
                        threaded_lookup.get(name, "-")
                    ),
                    "Status": (
                        "✅ Success"
                        if error is None
                        else "❌ Failed"
                    ),
                }
            )

        weather_df = pd.DataFrame(rows)

        st.dataframe(
            weather_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="📥 Download Results as CSV",
            data=weather_df.to_csv(index=False),
            file_name="weather_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ================= BEFORE RUN ================= #

else:

    with dashboard_tab:

        st.info(
            """
👈 Configure the number of cities and threads from the sidebar,
then click **Run Benchmark**.

The dashboard will compare Sequential vs Concurrent execution
using live weather API requests.
"""
        )

    with weather_tab:

        st.info(
            "Weather data will appear here after running the benchmark."
        )

# ================= ABOUT TAB ================= #
# ================= BENCHMARK HISTORY ================= #

with history_tab:

    st.subheader("📜 Benchmark History")

    if st.session_state.history:

        history_df = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No benchmark runs yet. Run the benchmark to see history.")

with about_tab:

    st.header("📘 About This Project")

    st.markdown("""
## 🎯 Objective

This project demonstrates the performance difference between
Sequential execution and Concurrent execution using Python's
**ThreadPoolExecutor**.

Instead of making API requests one after another,
multiple weather requests are executed simultaneously,
significantly reducing total execution time.

---

## 🛠 Tech Stack

- Python
- Streamlit
- Requests
- Pandas
- Plotly
- ThreadPoolExecutor
- Open-Meteo API

---

## 📚 Concepts Demonstrated

- Multithreading
- Concurrency
- ThreadPoolExecutor
- REST API Integration
- Performance Benchmarking
- I/O Bound Operations
- Interactive Data Visualization

---

## 🌍 Real-world Applications

- Weather Monitoring Systems
- Stock Market Data Collection
- Web Scraping Pipelines
- Data Engineering Workflows
- Microservices
- Distributed Systems

---

## 🏆 Key Learning

Python threads are highly effective for
**I/O-bound tasks** because they overlap waiting time,
allowing multiple network requests to progress simultaneously.

This project demonstrates that concurrency can reduce execution
time dramatically without changing the core business logic.
""")

# ================= FOOTER ================= #

st.divider()

st.markdown(
"""
<div style='text-align:center;color:gray;font-size:15px'>

Built with ❤️ using

<b>Python</b> •
<b>Streamlit</b> •
<b>Plotly</b> •
<b>ThreadPoolExecutor</b> •
<b>Requests</b> •
<b>Open-Meteo API</b>

<br><br>

© 2026 Shivani Lokinindi

</div>
""",
unsafe_allow_html=True,
)