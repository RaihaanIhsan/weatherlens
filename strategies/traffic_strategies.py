# import joblib
# import pandas as pd
# from datetime import datetime
# from strategies.base_strategy import BaseStrategy
# from weather.weather_data import WeatherData
# import config


# class MLTrafficStrategy(BaseStrategy):
#     """Uses the trained Random Forest model to predict congestion."""

#     def __init__(self):
#         self.model        = joblib.load(config.MODEL_PATH)
#         self.city_enc     = joblib.load(config.CITY_ENCODER_PATH)
#         self.country_enc  = joblib.load(config.COUNTRY_ENCODER_PATH)
#         self.features     = joblib.load(config.FEATURE_LIST_PATH)

#     def predict(self, data: WeatherData) -> dict:
#         now = datetime.now()
#         hour        = now.hour
#         day_of_week = now.weekday()
#         month       = now.month
#         is_rush     = 1 if hour in range(7, 10) or hour in range(17, 20) else 0
#         is_weekend  = 1 if day_of_week >= 5 else 0

#         city_info = config.CITIES.get(data.city, {})
#         rain_sensitivity = city_info.get("rain_sensitivity", 0.5)

#         try:
#             city_encoded    = self.city_enc.transform([data.city])[0]
#         except ValueError:
#             city_encoded    = 0

#         try:
#             country_encoded = self.country_enc.transform([data.country])[0]
#         except ValueError:
#             country_encoded = 0

#         row = pd.DataFrame([[
#             data.temperature, data.rainfall, data.windspeed,
#             data.visibility, data.humidity,
#             hour, day_of_week, month, is_rush, is_weekend,
#             city_encoded, country_encoded, rain_sensitivity
#         ]], columns=self.features)

#         prediction = self.model.predict(row)[0]
#         proba      = self.model.predict_proba(row)[0]
#         classes    = self.model.classes_
#         confidence = {c: round(float(p), 2) for c, p in zip(classes, proba)}

#         advice = {
#             "HIGH":   "Avoid highways. Expect 30–50 min delays. Use alternate routes.",
#             "MEDIUM": "Moderate slowdowns expected. Allow extra 15–20 mins.",
#             "LOW":    "Traffic flowing normally.",
#         }

#         return {
#             "congestion":  prediction,
#             "confidence":  confidence,
#             "advice":      advice.get(prediction, ""),
#             "is_rush_hour": bool(is_rush),
#         }


# class RuleBasedTrafficStrategy(BaseStrategy):
#     """Fallback strategy if ML model is unavailable."""

#     def predict(self, data: WeatherData) -> dict:
#         if data.rainfall > 15 or data.visibility < 1000:
#             level = "HIGH"
#         elif data.rainfall > 5 or data.windspeed > 40:
#             level = "MEDIUM"
#         else:
#             level = "LOW"

#         return {
#             "congestion": level,
#             "confidence": {},
#             "advice": f"Rule-based prediction for {data.city}.",
#             "is_rush_hour": False,
#         }

import joblib
import pandas as pd
from datetime import datetime
from strategies.base_strategy import BaseStrategy
from weather.weather_data import WeatherData
import config


class MLTrafficStrategy(BaseStrategy):
    def __init__(self):
        self.model       = joblib.load(config.MODEL_PATH)
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

    def predict(self, data: WeatherData) -> dict:
        row        = self._build_row(data)
        prediction = self.model.predict(row)[0]
        proba      = self.model.predict_proba(row)[0]
        classes    = self.model.classes_
        confidence = {c: round(float(p), 2) for c, p in zip(classes, proba)}

        advice = {
            "HIGH":   "Avoid highways. Expect 30–50 min delays. Use alternate routes.",
            "MEDIUM": "Moderate slowdowns expected. Allow extra 15–20 mins.",
            "LOW":    "Traffic flowing normally.",
        }

        now = datetime.now()
        return {
            "congestion":   prediction,
            "confidence":   confidence,
            "advice":       advice.get(prediction, ""),
            "is_rush_hour": now.hour in range(7,10) or now.hour in range(17,20),
        }


class RuleBasedTrafficStrategy(BaseStrategy):
    """Fallback if ML model unavailable."""
    def predict(self, data: WeatherData) -> dict:
        if data.rainfall > 15 or data.visibility < 1000:
            level = "HIGH"
        elif data.rainfall > 5 or data.windspeed > 40:
            level = "MEDIUM"
        else:
            level = "LOW"
        return {
            "congestion":   level,
            "confidence":   {},
            "advice":       f"Rule-based prediction for {data.city}.",
            "is_rush_hour": False,
        }