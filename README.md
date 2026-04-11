```markdown
# 🌦 Weather Impact Monitoring System

A real-time weather monitoring system that predicts the impact of weather on
traffic, energy demand, and retail behavior using machine learning and
OOP design patterns.

---

## ✨ Features

- **Live Weather** — fetches real-time data for any city via Open-Meteo API
- **Traffic Prediction** — congestion level (LOW/MEDIUM/HIGH) using Random Forest ML
- **Energy Prediction** — alert level + estimated demand change %
- **Retail Prediction** — surge level + items expected to spike in demand
- **Congestion Map** — interactive heatmap showing traffic intensity across the city
- **Historical Charts** — 5-panel Plotly chart over a custom date range
- **PDF Reports** — one-click downloadable report with all predictions
- **CLI Mode** — run everything from the terminal without the web UI

## 🧱 Design Patterns

| Pattern | Where |
|---|---|
| Singleton | `WeatherStation` |
| Observer | `WeatherStation` → all monitors |
| Strategy | ML model per monitor (swappable) |
| Decorator | Enriches raw weather data with severity + description |
| Factory Method | `ReportFactory` creates report by type |

---

## ⚙️ Setup

### 1. Clone & create virtual environment
```bash
git clone https://github.com/yourusername/DesignPattern_weatherForecastingSystem.git
cd DesignPattern_weatherForecastingSystem
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add ML models
Place all `.pkl` files in the `models/` folder:
```
models/
├── weather_traffic_model.pkl
├── weather_energy_model.pkl
├── weather_energy_regressor.pkl
├── weather_retail_model.pkl
├── city_encoder.pkl
├── country_encoder.pkl
└── feature_list.pkl
```
> Train models using the included Colab notebook.

### 4. Run
```bash
# Web UI
streamlit run gui/app.py

# CLI
python main.py
```

---

## 🌐 Data Source
[Open-Meteo](https://open-meteo.com/) — free, no API key required.

## 👩‍💻 Author
Raihaan Ihsan — SE, NED University (2022–2026)
```
