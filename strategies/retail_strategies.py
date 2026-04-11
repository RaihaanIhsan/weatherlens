# from strategies.base_strategy import BaseStrategy
# from weather.weather_data import WeatherData


# class RetailStrategy(BaseStrategy):
#     def predict(self, data: WeatherData) -> dict:
#         items = []
#         surge_level = "LOW"

#         if data.rainfall > 10:
#             items += ["umbrellas", "raincoats", "waterproof boots"]
#             surge_level = "HIGH"
#         elif data.rainfall > 2:
#             items += ["umbrellas", "light jackets"]
#             surge_level = "MEDIUM"

#         if data.temperature > 38:
#             items += ["cold drinks", "ice cream", "fans", "sunscreen"]
#             surge_level = "HIGH"
#         elif data.temperature > 28:
#             items += ["cold drinks", "sunscreen"]

#         if data.windspeed > 50:
#             items += ["generators", "emergency supplies", "candles"]
#             surge_level = "HIGH"

#         if data.temperature < 5:
#             items += ["heaters", "hot beverages", "blankets"]
#             surge_level = "MEDIUM" if surge_level == "LOW" else surge_level

#         items = list(dict.fromkeys(items))  # deduplicate

#         return {
#             "surge_level":    surge_level,
#             "demand_items":   items if items else ["No unusual demand expected"],
#             "advice": f"Stock up on: {', '.join(items)}" if items else "Normal inventory levels sufficient.",
#         }

import joblib
import pandas as pd
from datetime import datetime
from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData
import config


class RetailStrategy(BaseStrategy):
    def __init__(self):
        self.model       = joblib.load(config.RETAIL_MODEL_PATH)
        self.city_enc    = joblib.load(config.CITY_ENCODER_PATH)
        self.country_enc = joblib.load(config.COUNTRY_ENCODER_PATH)
        self.features    = joblib.load(config.FEATURE_LIST_PATH)

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

    def _get_demand_items(self, data: WeatherData, surge_level: str) -> list:
        items = []
        t = data.temperature

        if data.rainfall > 10:
            items += ["umbrellas", "raincoats", "waterproof boots"]
        elif data.rainfall > 2:
            items += ["umbrellas", "light jackets"]

        if t > 38:
            items += ["cold drinks", "ice cream", "fans", "sunscreen"]
        elif t > 28:
            items += ["cold drinks", "sunscreen"]

        if t < 0:
            items += ["heaters", "hot beverages", "blankets", "winter coats"]
        elif t < 10:
            items += ["heaters", "hot beverages", "blankets"]

        if data.windspeed > 60:
            items += ["generators", "emergency supplies", "candles", "torches"]
        elif data.windspeed > 40:
            items += ["emergency supplies"]

        if getattr(data, "snowfall", 0) > 5:
            items += ["snow boots", "gloves", "shovels", "salt"]
        elif getattr(data, "snowfall", 0) > 0:
            items += ["snow boots", "gloves"]

        items = list(dict.fromkeys(items))  # deduplicate
        return items if items else ["No unusual demand expected"]

    def predict(self, data: WeatherData) -> dict:
        row        = self._build_row(data)
        surge      = self.model.predict(row)[0]
        proba      = self.model.predict_proba(row)[0]
        classes    = self.model.classes_
        confidence = {c: round(float(p), 2) for c, p in zip(classes, proba)}
        items      = self._get_demand_items(data, surge)

        advice = {
            "HIGH":   f"Urgent restock needed: {', '.join(items[:3])}.",
            "MEDIUM": f"Monitor stock levels for: {', '.join(items[:3])}.",
            "LOW":    "Normal inventory levels sufficient.",
        }

        return {
            "surge_level":  surge,
            "demand_items": items,
            "confidence":   confidence,
            "advice":       advice.get(surge, ""),
        }