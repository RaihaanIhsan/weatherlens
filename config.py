# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Model paths
# MODEL_PATH        = os.path.join(BASE_DIR, "models", "weather_traffic_model.pkl")
# CITY_ENCODER_PATH = os.path.join(BASE_DIR, "models", "city_encoder.pkl")
# COUNTRY_ENCODER_PATH = os.path.join(BASE_DIR, "models", "country_encoder.pkl")
# FEATURE_LIST_PATH = os.path.join(BASE_DIR, "models", "feature_list.pkl")

# # Supported cities
# CITIES = {
#     "Karachi":    {"lat": 24.86, "lon": 67.01, "country": "PK", "rain_sensitivity": 0.95},
#     "Lahore":     {"lat": 31.55, "lon": 74.35, "country": "PK", "rain_sensitivity": 0.80},
#     "Islamabad":  {"lat": 33.72, "lon": 73.06, "country": "PK", "rain_sensitivity": 0.75},
#     "London":     {"lat": 51.51, "lon": -0.13, "country": "GB", "rain_sensitivity": 0.35},
#     "Manchester": {"lat": 53.48, "lon": -2.24, "country": "GB", "rain_sensitivity": 0.30},
#     "New York":   {"lat": 40.71, "lon": -74.01,"country": "US", "rain_sensitivity": 0.45},
#     "Chicago":    {"lat": 41.88, "lon": -87.63,"country": "US", "rain_sensitivity": 0.50},
#     "Colombo":    {"lat": 6.93,  "lon": 79.85, "country": "LK", "rain_sensitivity": 0.40},
#     "Kandy":      {"lat": 7.29,  "lon": 80.63, "country": "LK", "rain_sensitivity": 0.45},
# }

# REPORTS_DIR = os.path.join(BASE_DIR, "reports_output")
# os.makedirs(REPORTS_DIR, exist_ok=True)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths

MODEL_PATH            = os.path.join(BASE_DIR, "models", "weather_traffic_model.pkl")
ENERGY_MODEL_PATH     = os.path.join(BASE_DIR, "models",  "weather_energy_model.pkl")
ENERGY_REGRESSOR_PATH = os.path.join(BASE_DIR, "models", "weather_energy_regressor.pkl")
RETAIL_MODEL_PATH     = os.path.join(BASE_DIR, "models", "weather_retail_model.pkl")
CITY_ENCODER_PATH     = os.path.join(BASE_DIR, "models", "city_encoder.pkl")
COUNTRY_ENCODER_PATH  = os.path.join(BASE_DIR, "models", "country_encoder.pkl")
FEATURE_LIST_PATH     = os.path.join(BASE_DIR, "models", "feature_list.pkl")

# Supported cities
CITIES = {
    "Karachi":    {"lat": 24.86, "lon": 67.01, "country": "PK", "rain_sensitivity": 0.95, "population_density": 0.95},
    "Lahore":     {"lat": 31.55, "lon": 74.35, "country": "PK", "rain_sensitivity": 0.80, "population_density": 0.85},
    "Islamabad":  {"lat": 33.72, "lon": 73.06, "country": "PK", "rain_sensitivity": 0.75, "population_density": 0.60},
    "London":     {"lat": 51.51, "lon": -0.13, "country": "GB", "rain_sensitivity": 0.35, "population_density": 0.80},
    "Manchester": {"lat": 53.48, "lon": -2.24, "country": "GB", "rain_sensitivity": 0.30, "population_density": 0.70},
    "New York":   {"lat": 40.71, "lon": -74.01,"country": "US", "rain_sensitivity": 0.45, "population_density": 0.90},
    "Chicago":    {"lat": 41.88, "lon": -87.63,"country": "US", "rain_sensitivity": 0.50, "population_density": 0.75},
    "Colombo":    {"lat": 6.93,  "lon": 79.85, "country": "LK", "rain_sensitivity": 0.40, "population_density": 0.65},
    "Kandy":      {"lat": 7.29,  "lon": 80.63, "country": "LK", "rain_sensitivity": 0.45, "population_density": 0.50},
}

REPORTS_DIR = os.path.join(BASE_DIR, "reports_output")
os.makedirs(REPORTS_DIR, exist_ok=True)