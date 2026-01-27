# -*- coding: utf-8 -*-
import datetime
import esdl
from esdl import EnergySystem
import helics as h
from dots_infrastructure.DataClasses import TimeStepInformation, EsdlId
from dots_infrastructure.Logger import LOGGER
import pandas as pd

from WeatherService.weather_service_base import WeatherServiceBase

class CalculationServiceWeather(WeatherServiceBase):

    def parse_profile(self, profile : esdl.DateTimeProfile):
        # Parse the profile and return the values
        from_profile = []
        to_profile = []
        value_profile = []
        for el in profile.element:
            value_profile.append(el.value)
            from_profile.append(el.from_)
            to_profile.append(el.to)
        
        ret_val = pd.DataFrame({
            "from": from_profile,
            "to": to_profile,
            "value": value_profile
        })
        ret_val.set_index("from", inplace=True)
        return ret_val

    def init_calculation_service(self, energy_system: esdl.EnergySystem):
        LOGGER.info("init calculation service")
        # set windowsizes for different calculations
        self.window_size_in_seconds = 43200
        self.step_size_in_seconds = 900

        for esdl_id in self.simulator_configuration.esdl_ids:
            # set in setup
            self.solar_irradiances: dict[esdl_id, pd.DataFrame] = {}
            self.air_temperatures:  dict[esdl_id, pd.DataFrame] = {}
            self.soil_temperatures: dict[esdl_id, pd.DataFrame] = {}

            # Get profiles from the ESDL
            for obj in energy_system.eAllContents():
                if hasattr(obj, "id") and obj.id == esdl_id:
                    environmental_profiles = obj

            solar_irradiance_profile = environmental_profiles.solarIrradianceProfile
            air_temperature_profile  = environmental_profiles.outsideTemperatureProfile
            soil_temperature_profile = environmental_profiles.soilTemperatureProfile

            self.solar_irradiances[esdl_id] = self.parse_profile(solar_irradiance_profile)
            self.air_temperatures[esdl_id]  = self.parse_profile(air_temperature_profile)
            self.soil_temperatures[esdl_id] = self.parse_profile(soil_temperature_profile)

    def weather_prediction(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):

        to_date_time = simulation_time + datetime.timedelta(seconds=self.window_size_in_seconds - 1)
        predicted_solar_irradiances = self.solar_irradiances[esdl_id][
                                      simulation_time:to_date_time]["value"].tolist()
        predicted_air_temperatures = self.air_temperatures[esdl_id][
                                     simulation_time:to_date_time]["value"].tolist()
        predicted_soil_temperatures = self.soil_temperatures[esdl_id][
                                      simulation_time:to_date_time]["value"].tolist()

        ret_val = {}
        ret_val["solar_irradiance"] = predicted_solar_irradiances
        ret_val["air_temperature"] = predicted_air_temperatures
        ret_val["soil_temperature"] = predicted_soil_temperatures

        return ret_val

    def current_current_weather_data(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        to_date_time = simulation_time + datetime.timedelta(seconds=self.step_size_in_seconds - 1)
        current_solar_irradiances = self.solar_irradiances[esdl_id][
                                      simulation_time:to_date_time]["value"][0]
        current_air_temperatures = self.air_temperatures[esdl_id][
                                     simulation_time:to_date_time]["value"][0]
        current_soil_temperatures = self.soil_temperatures[esdl_id][
                                      simulation_time:to_date_time]["value"][0]

        ret_val = {}
        ret_val["current_solar_irradiance"] = current_solar_irradiances
        ret_val["current_air_temperature"] = current_air_temperatures
        ret_val["current_soil_temperature"] = current_soil_temperatures

        return ret_val

if __name__ == "__main__":

    helics_simulation_executor = CalculationServiceWeather()
    helics_simulation_executor.start_simulation()
    helics_simulation_executor.stop_simulation()
