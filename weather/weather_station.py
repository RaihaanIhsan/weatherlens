# from __future__ import annotations
# from typing import List
# from weather.weather_data import WeatherData


# class WeatherStation:
#     """
#     Singleton + Observer Subject.
#     Only one instance exists. Notifies all registered observers on update.
#     """
#     _instance: WeatherStation | None = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._observers = []
#             cls._instance._current_data = None
#         return cls._instance

#     def register(self, observer):
#         self._observers.append(observer)

#     def unregister(self, observer):
#         self._observers.remove(observer)

#     def notify_all(self):
#         for observer in self._observers:
#             observer.update(self._current_data)

#     def set_weather(self, data: WeatherData):
#         self._current_data = data
#         self.notify_all()

#     @property
#     def current_data(self):
#         return self._current_data


from __future__ import annotations
from typing import List, Optional
from weather.weather_data import WeatherData


class WeatherStation:
    _instance: Optional['WeatherStation'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers = []
            cls._instance._current_data = None
        return cls._instance

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify_all(self):
        for observer in self._observers:
            observer.update(self._current_data)

    def set_weather(self, data: WeatherData):
        self._current_data = data
        self.notify_all()

    @property
    def current_data(self):
        return self._current_data