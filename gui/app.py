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

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather.weather_station import WeatherStation
from monitors.traffic_monitor import TrafficMonitor
from monitors.energy_monitor import EnergyMonitor
from monitors.retail_monitor import RetailMonitor
from strategies.traffic_strategies import MLTrafficStrategy, RuleBasedTrafficStrategy
from strategies.energy_strategies import EnergyStrategy
from strategies.retail_strategies import RetailStrategy
from reports.report_factory import ReportFactory
from api.weather_api import fetch_live_weather
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
    }
    .card-value {
        font-size: 22px;
        font-weight: 700;
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
st.title("🌦 Weather Impact Monitoring System")
st.caption("Real-time weather → traffic, energy & retail predictions")

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

    st.markdown("### 📍 Current Weather")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🌡 Temperature", f"{w.temperature}°C")
    c2.metric("🌧 Rainfall",    f"{w.rainfall} mm")
    c3.metric("💨 Wind Speed",  f"{w.windspeed} km/h")
    c4.metric("👁 Visibility",  f"{int(w.visibility)} m")
    c5.metric("💧 Humidity",    f"{w.humidity}%")
    c6.metric("⚠️ Severity",    w.severity)

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
        st.markdown("#### 🚦 Traffic")
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
                f'<div class="card-title">Rush Hour</div>'
                f'<div class="card-value">{"🔴 Yes" if t.get("is_rush_hour") else "🟢 No"}</div>'
                f'</div>', unsafe_allow_html=True
            )
            if t.get("confidence"):
                st.markdown("**Model confidence:**")
                for label, prob in t["confidence"].items():
                    st.progress(prob, text=f"{label}: {prob:.0%}")
            st.info(t.get("advice", ""))

    # Energy
    with col2:
        st.markdown("#### ⚡ Energy")
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
        st.markdown("#### 🛒 Retail")
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
                cols[i % 2].markdown(f"✅ {item}")
            st.info(r.get("advice", ""))

    # ── PDF Report ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📄 Generate Report")

    if st.button("📥 Generate PDF Report", type="primary"):
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
    st.info("👈 Select a city from the sidebar and click **Fetch Live Weather** to begin.")