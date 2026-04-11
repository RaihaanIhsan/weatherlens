# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# import threading
# import os

# from weather.weather_station import WeatherStation
# from monitors.traffic_monitor import TrafficMonitor
# from monitors.energy_monitor import EnergyMonitor
# from monitors.retail_monitor import RetailMonitor
# from strategies.traffic_strategies import MLTrafficStrategy, RuleBasedTrafficStrategy
# from strategies.energy_strategies import EnergyStrategy
# from strategies.retail_strategies import RetailStrategy
# from reports.report_factory import ReportFactory
# from api.weather_api import fetch_live_weather
# import config


# class WeatherApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Weather Impact Monitoring System")
#         self.root.geometry("820x640")
#         self.root.configure(bg="#1a1a2e")

#         self._setup_station()
#         self._build_ui()

#     def _setup_station(self):
#         self.station = WeatherStation()
#         try:
#             traffic_strategy = MLTrafficStrategy()
#         except Exception:
#             traffic_strategy = RuleBasedTrafficStrategy()

#         self.traffic = TrafficMonitor(traffic_strategy)
#         self.energy  = EnergyMonitor(EnergyStrategy())
#         self.retail  = RetailMonitor(RetailStrategy())

#         self.station.register(self.traffic)
#         self.station.register(self.energy)
#         self.station.register(self.retail)

#     def _build_ui(self):
#         # Header
#         header = tk.Frame(self.root, bg="#0f3460", pady=12)
#         header.pack(fill="x")
#         tk.Label(header, text="🌦  Weather Impact Monitoring System",
#                  font=("Helvetica", 16, "bold"),
#                  bg="#0f3460", fg="white").pack()

#         # Input row
#         input_frame = tk.Frame(self.root, bg="#16213e", pady=10, padx=16)
#         input_frame.pack(fill="x")

#         tk.Label(input_frame, text="City:", bg="#16213e", fg="white",
#                  font=("Helvetica", 11)).pack(side="left")

#         self.city_var = tk.StringVar(value="Karachi")
#         city_options = list(config.CITIES.keys())
#         self.city_combo = ttk.Combobox(input_frame, textvariable=self.city_var,
#                                         values=city_options, width=18,
#                                         font=("Helvetica", 11))
#         self.city_combo.pack(side="left", padx=8)

#         # allow typing any city
#         self.city_combo.configure(state="normal")

#         tk.Button(input_frame, text="Fetch Weather",
#                   command=self._fetch_weather,
#                   bg="#e63946", fg="white", font=("Helvetica", 10, "bold"),
#                   relief="flat", padx=12, pady=4).pack(side="left", padx=6)

#         tk.Button(input_frame, text="Generate PDF Report",
#                   command=self._generate_report,
#                   bg="#2a9d8f", fg="white", font=("Helvetica", 10, "bold"),
#                   relief="flat", padx=12, pady=4).pack(side="left", padx=6)

#         # Weather summary strip
#         self.summary_var = tk.StringVar(value="No data yet.")
#         summary_bar = tk.Frame(self.root, bg="#0f3460", pady=6, padx=16)
#         summary_bar.pack(fill="x")
#         tk.Label(summary_bar, textvariable=self.summary_var,
#                  bg="#0f3460", fg="#a8dadc",
#                  font=("Helvetica", 10)).pack(anchor="w")

#         # Tabs for each monitor
#         notebook = ttk.Notebook(self.root)
#         notebook.pack(fill="both", expand=True, padx=10, pady=8)

#         self.traffic_text = self._make_tab(notebook, "Traffic")
#         self.energy_text  = self._make_tab(notebook, "Energy")
#         self.retail_text  = self._make_tab(notebook, "Retail")
#         self.log_text     = self._make_tab(notebook, "Log")

#     def _make_tab(self, notebook, label):
#         frame = ttk.Frame(notebook)
#         notebook.add(frame, text=f"  {label}  ")
#         text = scrolledtext.ScrolledText(frame, wrap="word",
#                                           font=("Courier", 10),
#                                           bg="#0d0d1a", fg="#e0e0e0",
#                                           insertbackground="white",
#                                           relief="flat", padx=10, pady=10)
#         text.pack(fill="both", expand=True)
#         return text

#     def _fetch_weather(self):
#         city = self.city_var.get().strip()
#         if not city:
#             messagebox.showwarning("Input needed", "Please enter a city name.")
#             return
#         self._log(f"Fetching weather for {city}...")
#         threading.Thread(target=self._fetch_thread, args=(city,), daemon=True).start()

#     def _fetch_thread(self, city):
#         data = fetch_live_weather(city)
#         if not data:
#             self._log(f"Could not fetch weather for '{city}'.")
#             return

#         self.root.after(0, lambda: self._update_ui(data))

#     def _update_ui(self, data):
#         self.summary_var.set(
#             f"{data.city}, {data.country}  |  {data.temperature}°C  |  "
#             f"Rain: {data.rainfall}mm  |  Wind: {data.windspeed}km/h  |  "
#             f"Severity: {data.severity}  |  {data.description.capitalize()}"
#         )

#         self.station.set_weather(data)

#         self._write_tab(self.traffic_text, self.traffic.last_result)
#         self._write_tab(self.energy_text,  self.energy.last_result)
#         self._write_tab(self.retail_text,  self.retail.last_result)
#         self._log(f"Updated: {data.city} @ {data.timestamp.strftime('%H:%M:%S')}")

#     def _write_tab(self, widget, result: dict):
#         widget.configure(state="normal")
#         widget.delete("1.0", "end")
#         if not result:
#             widget.insert("end", "No data.")
#         else:
#             for k, v in result.items():
#                 if isinstance(v, dict):
#                     v = "\n    " + "\n    ".join(f"{a}: {b}" for a, b in v.items())
#                 elif isinstance(v, list):
#                     v = ", ".join(str(i) for i in v)
#                 widget.insert("end", f"{k.replace('_',' ').upper():<20} {v}\n\n")
#         widget.configure(state="disabled")

#     def _generate_report(self):
#         if not self.station.current_data:
#             messagebox.showwarning("No data", "Fetch weather data first.")
#             return
#         try:
#             factory = ReportFactory()
#             report  = factory.create("pdf")
#             path    = report.generate(
#                 self.station.current_data,
#                 [self.traffic, self.energy, self.retail]
#             )
#             self._log(f"PDF saved → {path}")
#             messagebox.showinfo("Report Ready", f"PDF saved to:\n{path}")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def _log(self, msg):
#         self.log_text.configure(state="normal")
#         from datetime import datetime
#         self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
#         self.log_text.see("end")
#         self.log_text.configure(state="disabled")


# def run_gui():
#     root = tk.Tk()
#     app = WeatherApp(root)
#     root.mainloop()
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
from api.historical_api import (
    fetch_historical_weather,
    compute_derived_metrics,
    resample_daily
)



from weather.weather_station import WeatherStation
from monitors.traffic_monitor import TrafficMonitor
from monitors.energy_monitor import EnergyMonitor
from monitors.retail_monitor import RetailMonitor
from strategies.traffic_strategies import MLTrafficStrategy, RuleBasedTrafficStrategy
from strategies.energy_strategies import EnergyStrategy
from strategies.retail_strategies import RetailStrategy
from reports.report_factory import ReportFactory
from api.weather_api import fetch_live_weather
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
from api.historical_api import (
    fetch_historical_weather,
    compute_derived_metrics,
    resample_daily
)
import config


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather Impact Monitor",
    page_icon="🌦",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    .traffic-card  { border-color: #e63946; }
    .energy-card   { border-color: #f4a261; }
    .retail-card   { border-color: #2a9d8f; }
    .weather-card  { border-color: #4895ef; }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
        opacity: 0.75;
        color: #ffffff;
    }
    .card-value {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
    }
    .severity-EXTREME { color: #e63946; }
    .severity-HIGH    { color: #f4a261; }
    .severity-MODERATE{ color: #ffd166; }
    .severity-LOW     { color: #2a9d8f; }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-HIGH     { background: #e6394622; color: #e63946; border: 1px solid #e63946; }
    .badge-MEDIUM   { background: #f4a26122; color: #f4a261; border: 1px solid #f4a261; }
    .badge-LOW      { background: #2a9d8f22; color: #2a9d8f; border: 1px solid #2a9d8f; }
    .badge-EXTREME  { background: #e6394644; color: #ff6b6b; border: 1px solid #ff6b6b; }
</style>
""", unsafe_allow_html=True)


# ── Session state setup ────────────────────────────────────────────────────────
@st.cache_resource
def get_station_and_monitors():
    station = WeatherStation()

    try:
        traffic_strategy = MLTrafficStrategy()
    except Exception:
        traffic_strategy = RuleBasedTrafficStrategy()

    traffic = TrafficMonitor(traffic_strategy)
    energy  = EnergyMonitor(EnergyStrategy())
    retail  = RetailMonitor(RetailStrategy())

    station.register(traffic)
    station.register(energy)
    station.register(retail)

    return station, traffic, energy, retail

def build_charts(daily_df: pd.DataFrame, city: str) -> go.Figure:
    """Build a mixed line + bar Plotly figure with 5 subplots."""

    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(
            "Temperature (°C)",
            "Rainfall (mm/day)",
            "Wind Speed (km/h)",
            "Congestion Level",
            "Energy Demand Change (%)",
        )
    )

    dates = daily_df["datetime"]

    # ── 1. Temperature — line ────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=dates, y=daily_df["temperature"],
        mode="lines", name="Temperature",
        line=dict(color="#4895ef", width=2),
        fill="tozeroy",
        fillcolor="rgba(72,149,239,0.1)",
    ), row=1, col=1)

    # ── 2. Rainfall — bar ────────────────────────────────────────────────────
    fig.add_trace(go.Bar(
        x=dates, y=daily_df["rainfall"],
        name="Rainfall",
        marker_color="rgba(100,180,255,0.7)",
        marker_line_color="#4895ef",
        marker_line_width=0.5,
    ), row=2, col=1)

    # ── 3. Wind speed — line ─────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=dates, y=daily_df["windspeed"],
        mode="lines", name="Wind Speed",
        line=dict(color="#a8dadc", width=2),
    ), row=3, col=1)

    # ── 4. Congestion — bar (color-coded) ────────────────────────────────────
    congestion_colors = daily_df["congestion_label"].map({
        "LOW":    "rgba(42,157,143,0.75)",
        "MEDIUM": "rgba(244,162,97,0.75)",
        "HIGH":   "rgba(230,57,70,0.75)",
    })

    fig.add_trace(go.Bar(
        x=dates,
        y=daily_df["congestion_numeric"],
        name="Congestion",
        marker_color=congestion_colors,
        marker_line_width=0,
        customdata=daily_df["congestion_label"],
        hovertemplate="Date: %{x}<br>Level: %{customdata}<extra></extra>",
    ), row=4, col=1)

    # Congestion y-axis ticks
    fig.update_yaxes(
        tickvals=[1, 2, 3],
        ticktext=["LOW", "MED", "HIGH"],
        row=4, col=1
    )

    # ── 5. Energy demand — line + fill ───────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=dates, y=daily_df["energy_demand_pct"],
        mode="lines", name="Energy Demand",
        line=dict(color="#f4a261", width=2),
        fill="tozeroy",
        fillcolor="rgba(244,162,97,0.1)",
    ), row=5, col=1)

    # ── Layout ───────────────────────────────────────────────────────────────
    fig.update_layout(
        height=900,
        title_text=f"Historical Weather & Impact — {city}",
        title_font=dict(size=16, color="#ffffff"),
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="#c0c0c0", size=11),
        showlegend=False,
        margin=dict(l=60, r=20, t=80, b=40),
        hovermode="x unified",
    )

    # Gridlines
    for i in range(1, 6):
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#1e2130",
            tickfont=dict(color="#888"),
            row=i, col=1
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor="#1e2130",
            tickfont=dict(color="#888"),
            row=i, col=1
        )

    return fig

station, traffic_mon, energy_mon, retail_mon = get_station_and_monitors()

# ── Helper: badge html ─────────────────────────────────────────────────────────
def badge(level: str) -> str:
    return f'<span class="badge badge-{level}">{level}</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌦 Weather Monitor")
    st.markdown("---")

    city_options = list(config.CITIES.keys())
    selected_city = st.selectbox("Select a city", city_options)

    custom_city = st.text_input("Or type any city", placeholder="e.g. Tokyo, Dubai...")
    city = custom_city.strip() if custom_city.strip() else selected_city

    fetch_btn = st.button("🔄 Fetch Live Weather", use_container_width=True, type="primary")

    st.markdown("---")
    st.caption("Data source: Open-Meteo API")
    st.caption("Model: Random Forest (scikit-learn)")


# ── Main content ───────────────────────────────────────────────────────────────
st.title("Weather Impact Monitoring System")
# st.caption("Real-time weather → traffic, energy & retail predictions")

if fetch_btn:
    with st.spinner(f"Fetching live weather for {city}..."):
        data = fetch_live_weather(city)

    if not data:
        st.error(f"Could not find weather data for '{city}'. Try another city name.")
    else:
        station.set_weather(data)
        st.session_state["weather_data"] = data
        st.session_state["traffic"] = traffic_mon.last_result
        st.session_state["energy"]  = energy_mon.last_result
        st.session_state["retail"]  = retail_mon.last_result
        st.success(f"Weather updated for **{city}**")


# ── Weather summary ────────────────────────────────────────────────────────────
if "weather_data" in st.session_state:
    w = st.session_state["weather_data"]

    st.markdown("### Current Weather")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Temperature", f"{w.temperature}°C")
    c2.metric("Rainfall",    f"{w.rainfall} mm")
    c3.metric("Wind Speed",  f"{w.windspeed} km/h")
    c4.metric("Visibility",  f"{int(w.visibility)} m")
    c5.metric("Humidity",    f"{w.humidity}%")
    c6.metric("Severity",    w.severity)

    st.markdown(
        f"**Conditions:** {w.description.capitalize() or 'Clear'} &nbsp;|&nbsp; "
        f"**Country:** {w.country} &nbsp;|&nbsp; "
        f"**Time:** {w.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── Monitor results ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    # Traffic
    with col1:
        st.markdown("#### Traffic")
        t = st.session_state.get("traffic", {})
        if t:
            st.markdown(
                f'<div class="metric-card traffic-card">'
                f'<div class="card-title">Congestion Level</div>'
                f'<div class="card-value">{badge(t.get("congestion","—"))}</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-card traffic-card">'
                f'<div class="card-title fontcolor: #ffffff;">Rush Hour</div>'
                f'<div class="card-value">{"Yes" if t.get("is_rush_hour") else "No"}</div>'
                f'</div>', unsafe_allow_html=True
            )
            if t.get("confidence"):
                st.markdown("**Model confidence:**")
                for label, prob in t["confidence"].items():
                    st.progress(prob, text=f"{label}: {prob:.0%}")
            st.info(t.get("advice", ""))

    # Energy
    with col2:
        st.markdown("#### Energy")
        e = st.session_state.get("energy", {})
        if e:
            st.markdown(
                f'<div class="metric-card energy-card">'
                f'<div class="card-title">Alert Level</div>'
                f'<div class="card-value">{badge(e.get("alert_level","—"))}</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-card energy-card">'
                f'<div class="card-title">Demand Change</div>'
                f'<div class="card-value">+{e.get("demand_change_pct", 0)}%</div>'
                f'</div>', unsafe_allow_html=True
            )
            if e.get("reasons"):
                st.markdown("**Reasons:**")
                for r in e["reasons"]:
                    st.markdown(f"- {r}")
            st.info(e.get("advice", ""))

    # Retail
    with col3:
        st.markdown("####  Retail")
        r = st.session_state.get("retail", {})
        if r:
            st.markdown(
                f'<div class="metric-card retail-card">'
                f'<div class="card-title">Surge Level</div>'
                f'<div class="card-value">{badge(r.get("surge_level","—"))}</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown("**Items in demand:**")
            items = r.get("demand_items", [])
            cols = st.columns(2)
            for i, item in enumerate(items):
                cols[i % 2].markdown(f" {item}")
            st.info(r.get("advice", ""))

    # ── Map View ──────────────────────────────────────────────────────────────
    st.markdown("### 🗺️ Congestion Map")

    import pydeck as pdk

    city_info = config.CITIES.get(w.city)
    if city_info:
        congestion   = st.session_state.get("traffic", {}).get("congestion", "LOW")
        weight_map   = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.15}
        color_map    = {
            "HIGH":   [230, 57,  70,  220],
            "MEDIUM": [244, 162, 97,  220],
            "LOW":    [42,  157, 143, 220],
        }
        weight       = weight_map.get(congestion, 0.2)
        marker_color = color_map.get(congestion, [100, 100, 100, 220])

        # Generate heatmap points spread around the city center
        import numpy as np
        np.random.seed(42)
        n_points   = {"HIGH": 120, "MEDIUM": 60, "LOW": 25}.get(congestion, 30)
        spread     = {"HIGH": 0.06, "MEDIUM": 0.04, "LOW": 0.02}.get(congestion, 0.03)

        lats = np.random.normal(city_info["lat"], spread, n_points)
        lons = np.random.normal(city_info["lon"], spread, n_points)
        weights = np.random.uniform(weight * 0.5, weight, n_points)

        heat_df = pd.DataFrame({
            "lat":    lats,
            "lon":    lons,
            "weight": weights,
        })

        # Center marker df
        marker_df = pd.DataFrame([{
            "lat":   city_info["lat"],
            "lon":   city_info["lon"],
            "info":  f"{w.city} | {w.temperature}°C | {w.rainfall}mm rain | Congestion: {congestion}",
            "color": marker_color,
        }])

        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=heat_df,
            get_position=["lon", "lat"],
            get_weight="weight",
            radiusPixels=60,
            intensity=1.2,
            threshold=0.05,
            colorRange=[
                [42,  157, 143, 180],   # teal   → LOW
                [100, 200, 100, 200],   # green
                [255, 255, 0,   210],   # yellow → MEDIUM
                [255, 165, 0,   220],   # orange
                [230, 57,  70,  240],   # red    → HIGH
            ],
        )

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=marker_df,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_line_color=[255, 255, 255, 255],
            get_radius=600,
            line_width_min_pixels=2,
            pickable=True,
            stroked=True,
            auto_highlight=True,
        )

        view = pdk.ViewState(
            latitude=city_info["lat"],
            longitude=city_info["lon"],
            zoom=11,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[heatmap_layer, scatter_layer],
            initial_view_state=view,
            tooltip={"text": "{info}"},
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        ))

        # ── Legend ────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex; align-items:center; gap:24px; margin-top:8px;
                    background:#1e2130; padding:10px 16px; border-radius:10px;">
            <span style="color:#a0aec0; font-size:12px; font-weight:600; letter-spacing:1px;">
                CONGESTION LEGEND
            </span>
            <span style="display:flex; align-items:center; gap:6px;">
                <span style="width:14px;height:14px;border-radius:50%;
                             background:#2a9d8f;display:inline-block;"></span>
                <span style="color:#e0e0e0; font-size:12px;">Low — traffic flowing normally</span>
            </span>
            <span style="display:flex; align-items:center; gap:6px;">
                <span style="width:14px;height:14px;border-radius:50%;
                             background:#f4a261;display:inline-block;"></span>
                <span style="color:#e0e0e0; font-size:12px;">Medium — minor slowdowns</span>
            </span>
            <span style="display:flex; align-items:center; gap:6px;">
                <span style="width:14px;height:14px;border-radius:50%;
                             background:#e63946;display:inline-block;"></span>
                <span style="color:#e0e0e0; font-size:12px;">High — major delays expected</span>
            </span>
            <span style="display:flex; align-items:center; gap:6px;">
                <span style="width:12px;height:12px;border-radius:50%;
                             background:white;display:inline-block;border:2px solid #888;"></span>
                <span style="color:#e0e0e0; font-size:12px;">City center</span>
            </span>
        </div>
        """, unsafe_allow_html=True)    
    # ── Historical Charts ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Historical Weather & Impact Charts")

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "From",
            value=date.today() - timedelta(days=30),
            max_value=date.today() - timedelta(days=1),
        )
    with col_end:
        end_date = st.date_input(
            "To",
            value=date.today() - timedelta(days=1),
            max_value=date.today() - timedelta(days=1),
        )

    if start_date >= end_date:
        st.warning("'From' date must be before 'To' date.")
    else:
        if st.button("Load Historical Charts", use_container_width=True):
            with st.spinner(f"Fetching historical data for {w.city}..."):
                raw_df = fetch_historical_weather(
                    w.city,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )

            if raw_df is None or raw_df.empty:
                st.error("Could not fetch historical data for this city.")
            else:
                city_info    = config.CITIES.get(w.city, {})
                sensitivity  = city_info.get("rain_sensitivity", 0.5)
                enriched_df  = compute_derived_metrics(raw_df, sensitivity)
                daily_df     = resample_daily(enriched_df)

                st.session_state["historical_df"]   = daily_df
                st.session_state["historical_city"] = w.city

    # Render chart if data exists in session
    if "historical_df" in st.session_state:
        fig = build_charts(
            st.session_state["historical_df"],
            st.session_state["historical_city"]
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary stats below chart
        df = st.session_state["historical_df"]
        st.markdown("#### Period Summary")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Avg Temperature", f"{df['temperature'].mean():.1f}°C")
        s2.metric("Total Rainfall",  f"{df['rainfall'].sum():.1f} mm")
        s3.metric("Avg Wind Speed",  f"{df['windspeed'].mean():.1f} km/h")
        s4.metric("High Congestion Days",
                  int((df["congestion_label"] == "HIGH").sum()))
    # ── PDF Report ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Generate Report")

    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                factory = ReportFactory()
                report  = factory.create("pdf")
                path    = report.generate(
                    station.current_data,
                    [traffic_mon, energy_mon, retail_mon]
                )
                with open(path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(path),
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success(f"Report ready!")
            except Exception as ex:
                st.error(f"Report error: {ex}")

else:
    st.info("Select a city from the sidebar and click **Fetch Live Weather** to begin.")