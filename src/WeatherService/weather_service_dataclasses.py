from dataclasses import dataclass
from typing import List

@dataclass
class WeatherPredictionOutput:
    solar_irradiance : List | None = None
    air_temperature : List | None = None
    soil_temperature : List | None = None

@dataclass
class CurrentCurrentWeatherDataOutput:
    solar_irradiance : float | None = None
    air_temperature : float | None = None
    soil_temperature : float | None = None

