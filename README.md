# Weather Dashboard

A Streamlit dashboard for comparing sequential and threaded weather fetching across multiple cities.

## Project structure

- app.py - compatibility entry point that imports the packaged app
- src/weather_dashboard/app.py - main Streamlit dashboard
- src/weather_dashboard/fetcher.py - weather fetching logic

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run with Docker

```bash
docker compose up --build
```

Then open http://localhost:8501
