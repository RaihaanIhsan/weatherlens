# from strategies.base_strategy import BaseStrategy
# from weather.weather_data import WeatherData


# class EnergyStrategy(BaseStrategy):
#     def predict(self, data: WeatherData) -> dict:
#         demand_change = 0
#         reasons = []

#         if data.temperature > 38:
#             demand_change += 35
#             reasons.append("extreme heat — AC surge")
#         elif data.temperature > 30:
#             demand_change += 20
#             reasons.append("high heat — elevated AC usage")
#         elif data.temperature < 5:
#             demand_change += 25
#             reasons.append("cold snap — heating surge")
#         elif data.temperature < 15:
#             demand_change += 10
#             reasons.append("cool weather — moderate heating")

#         if data.windspeed > 50:
#             demand_change += 5
#             reasons.append("strong winds affecting grid")

#         level = "HIGH" if demand_change >= 30 else "MEDIUM" if demand_change >= 10 else "LOW"

#         return {
#             "demand_change_pct": demand_change,
#             "alert_level":       level,
#             "reasons":           reasons,
#             "advice": f"Grid load expected to change by +{demand_change}%. "
#                       f"{'Alert operators.' if level == 'HIGH' else 'Monitor closely.' if level == 'MEDIUM' else 'Normal operations.'}",
#         }

import joblib
import pandas as pd
from datetime import datetime
from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData
import config


class EnergyStrategy(BaseStrategy):
    def __init__(self):
        self.model      = joblib.load(config.ENERGY_MODEL_PATH)
        self.regressor  = joblib.load(config.ENERGY_REGRESSOR_PATH)
        self.city_enc   = joblib.load(config.CITY_ENCODER_PATH)
        self.country_enc= joblib.load(config.COUNTRY_ENCODER_PATH)
        self.features   = joblib.load(config.FEATURE_LIST_PATH)

    def _build_row(self, data: WeatherData) -> pd.DataFrame:
        now         = datetime.now()
        hour        = now.hour
        dow         = now.weekday()
        month       = now.month
        season      = (0 if month in [12,1,2] else
                       1 if month in [3,4,5] else
                       2 if month in [6,7,8] else 3)
        is_rush     = 1 if hour in range(7,10) or hour in range(17,20) else 0
        is_weekend  = 1 if dow >= 5 else 0
        is_night    = 1 if hour < 6 or hour >= 22 else 0
        is_peak_eve = 1 if 18 <= hour <= 22 else 0

        city_info = config.CITIES.get(data.city, {})

        try:
            city_encoded    = self.city_enc.transform([data.city])[0]
        except ValueError:
            city_encoded    = 0
        try:
            country_encoded = self.country_enc.transform([data.country])[0]
        except ValueError:
            country_encoded = 0

        return pd.DataFrame([[
            data.temperature,
            getattr(data, "apparent_temperature", data.temperature),
            data.rainfall,
            data.windspeed,
            data.visibility,
            data.humidity,
            getattr(data, "cloudcover", 0),
            getattr(data, "snowfall", 0),
            hour, dow, month, season,
            is_rush, is_weekend, is_night, is_peak_eve,
            city_encoded, country_encoded,
            city_info.get("rain_sensitivity", 0.5),
            city_info.get("population_density", 0.5),
        ]], columns=self.features)

    def predict(self, data: WeatherData) -> dict:
        row        = self._build_row(data)
        alert      = self.model.predict(row)[0]
        demand_pct = round(float(self.regressor.predict(row)[0]), 1)
        proba      = self.model.predict_proba(row)[0]
        classes    = self.model.classes_
        confidence = {c: round(float(p), 2) for c, p in zip(classes, proba)}

        reasons = []
        t = data.temperature
        if t > 38:    reasons.append("extreme heat — AC surge")
        elif t > 30:  reasons.append("high heat — elevated AC usage")
        elif t < 5:   reasons.append("cold snap — heating surge")
        elif t < 15:  reasons.append("cool weather — moderate heating")
        if data.humidity > 80 and t > 25:
            reasons.append("high humidity amplifying cooling load")
        if data.windspeed > 50:
            reasons.append("strong winds affecting grid stability")
        if getattr(data, "snowfall", 0) > 0:
            reasons.append("snowfall driving heating demand")

        advice = {
            "HIGH":   f"Grid load up +{demand_pct}%. Alert operators immediately.",
            "MEDIUM": f"Demand up +{demand_pct}%. Monitor grid closely.",
            "LOW":    f"Normal operations. Estimated +{demand_pct}% change.",
        }

        return {
            "alert_level":      alert,
            "demand_change_pct": demand_pct,
            "confidence":       confidence,
            "reasons":          reasons,
            "advice":           advice.get(alert, ""),
        }