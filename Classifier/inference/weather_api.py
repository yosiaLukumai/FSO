from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import requests


class VisibilityClass(str, Enum):
    CLEAR      = "CLEAR"
    MEDIUM_FOG = "MEDIUM_FOG"
    HEAVY_FOG  = "HEAVY_FOG"


@dataclass
class WeatherData:
    visibility_m: int
    condition: str
    temperature_c: float
    humidity_pct: int
    visibility_class: VisibilityClass
    timestamp: datetime


class OpenWeatherMapClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    CLEAR_THRESHOLD_M      = 5_000
    MEDIUM_FOG_THRESHOLD_M = 1_000

    def __init__(self, api_key: str, timeout_s: int = 10) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key must be a non-empty string.")
        self._api_key   = api_key.strip()
        self._timeout_s = timeout_s

    def get_weather(self, lat: float, lon: float) -> WeatherData:
        params = {"lat": lat, "lon": lon, "appid": self._api_key, "units": "metric"}
        response = requests.get(self.BASE_URL, params=params, timeout=self._timeout_s)
        response.raise_for_status()
        return self._parse_response(response.json())

    def get_visibility_class(self, lat: float, lon: float) -> VisibilityClass:
        return self.get_weather(lat, lon).visibility_class

    @staticmethod
    def visibility_to_class(visibility_m: int) -> VisibilityClass:
        if visibility_m > OpenWeatherMapClient.CLEAR_THRESHOLD_M:
            return VisibilityClass.CLEAR
        if visibility_m > OpenWeatherMapClient.MEDIUM_FOG_THRESHOLD_M:
            return VisibilityClass.MEDIUM_FOG
        return VisibilityClass.HEAVY_FOG

    def _parse_response(self, data: dict) -> WeatherData:
        visibility_m  = int(data.get("visibility", 0))
        condition     = data["weather"][0]["description"] if data.get("weather") else "unknown"
        temperature_c = float(data["main"]["temp"])
        humidity_pct  = int(data["main"]["humidity"])
        timestamp     = datetime.fromtimestamp(data.get("dt", 0), tz=timezone.utc)

        return WeatherData(
            visibility_m=visibility_m,
            condition=condition,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            visibility_class=self.visibility_to_class(visibility_m),
            timestamp=timestamp,
        )
