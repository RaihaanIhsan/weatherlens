import requests
import pandas as pd
from datetime import datetime
from api.weather_api import geocode_city


def fetch_historical_weather(city_name: str, start_date: str, end_date: str):
    """
    Fetch hourly historical weather from Open-Meteo archive API.
    start_date / end_date format: 'YYYY-MM-DD'
    Returns a cleaned DataFrame.
    """
    city_info = geocode_city(city_name)
    if not city_info:
        return None

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":  city_info["lat"],
        "longitude": city_info["lon"],
        "start_date": start_date,
        "end_date":   end_date,
        "hourly": (
            "temperature_2m,"
            "precipitation,"
            "windspeed_10m,"
            "visibility,"
            "relativehumidity_2m"
        ),
        "timezone": "auto",
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None

    hourly = resp.json().get("hourly", {})
    if not hourly:
        return None

    df = pd.DataFrame({
        "datetime":    pd.to_datetime(hourly["time"]),
        "temperature": hourly["temperature_2m"],
        "rainfall":    hourly["precipitation"],
        "windspeed":   hourly["windspeed_10m"],
        "visibility":  hourly["visibility"],
        "humidity":    hourly["relativehumidity_2m"],
    })

    df.fillna(0, inplace=True)
    return df


def compute_derived_metrics(df: pd.DataFrame, rain_sensitivity: float) -> pd.DataFrame:
    """
    Add congestion score and energy demand change columns
    using the same rule logic as the ML model labels.
    """
    df = df.copy()

    # Time features
    df["hour"]         = df["datetime"].dt.hour
    df["day_of_week"]  = df["datetime"].dt.dayofweek
    df["is_rush_hour"] = df["hour"].apply(
        lambda h: 1 if h in range(7, 10) or h in range(17, 20) else 0
    )
    df["is_weekend"] = df["day_of_week"].apply(lambda d: 1 if d >= 5 else 0)

    # Congestion score → label
    def congestion_score(row):
        score = row["rainfall"] * rain_sensitivity * 3
        if row["windspeed"] > 50:   score += 2
        elif row["windspeed"] > 30: score += 1
        if row["visibility"] < 1000:  score += 3
        elif row["visibility"] < 5000: score += 1
        if row["is_rush_hour"]: score *= 1.5
        if row["is_weekend"]:   score *= 0.6
        if row["temperature"] > 42 or row["temperature"] < -5: score += 1
        return score

    df["congestion_score"] = df.apply(congestion_score, axis=1)
    df["congestion_label"] = df["congestion_score"].apply(
        lambda s: "HIGH" if s >= 5 else "MEDIUM" if s >= 2 else "LOW"
    )
    df["congestion_numeric"] = df["congestion_label"].map(
        {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    )

    # Energy demand change
    def energy_demand(row):
        d = 0
        if row["temperature"] > 38:   d += 35
        elif row["temperature"] > 30: d += 20
        elif row["temperature"] < 5:  d += 25
        elif row["temperature"] < 15: d += 10
        if row["windspeed"] > 50:     d += 5
        return d

    df["energy_demand_pct"] = df.apply(energy_demand, axis=1)

    return df


def resample_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Resample hourly data to daily averages/sums for cleaner charts."""
    df = df.set_index("datetime")
    daily = pd.DataFrame({
        "temperature":        df["temperature"].resample("D").mean(),
        "rainfall":           df["rainfall"].resample("D").sum(),
        "windspeed":          df["windspeed"].resample("D").mean(),
        "humidity":           df["humidity"].resample("D").mean(),
        "congestion_numeric": df["congestion_numeric"].resample("D").mean(),
        "energy_demand_pct":  df["energy_demand_pct"].resample("D").mean(),
        "congestion_label":   df["congestion_label"].resample("D").agg(
            lambda x: x.value_counts().idxmax()
        ),
    }).reset_index()

    return daily