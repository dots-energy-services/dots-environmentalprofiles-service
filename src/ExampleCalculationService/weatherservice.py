# -*- coding: utf-8 -*-
from datetime import datetime
from esdl import esdl
import helics as h
import logging
from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SubscriptionDescription, TimeStepInformation, TimeRequestType
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from esdl import EnergySystem

class CalculationServiceWeather(HelicsSimulationExecutor):

    def __init__(self):
        super().__init__()

        publication_values = [
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="solar_irradiance",
                                   output_unit="Wm2",
                                   data_type=h.HelicsDataType.VECTOR),
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="air_temperature",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.VECTOR),
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="soil_temperature",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.VECTOR)
        ]

        weather_period_in_seconds = 900

        calculation_information = HelicsCalculationInformation(
            time_period_in_seconds=weather_period_in_seconds,
            offset=0,
            uninterruptible=False,
            wait_for_current_time_update=False,
            terminate_on_error=True,
            calculation_name="weather_prediction",
            inputs=[],
            outputs=publication_values,
            calculation_function=self.weather_prediction
        )
        self.add_calculation(calculation_information)

        publication_values = [
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="solar_irradiance_up_to_next_day",
                                   output_unit="Wm2",
                                   data_type=h.HelicsDataType.VECTOR),
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="air_temperature_up_to_next_day",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.VECTOR),
            PublicationDescription(global_flag=True,
                                   esdl_type="EnvironmentalProfiles",
                                   output_name="soil_temperature_up_to_next_day",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.VECTOR)
        ]

        weather_period_in_seconds = 900

        calculation_information_schedule = HelicsCalculationInformation(weather_period_in_seconds, 0, False, False,
                                                                        True, "weather_prediction_up_to_next_day", [],
                                                                        publication_values,
                                                                        self.weather_prediction_up_to_next_day)
        self.add_calculation(calculation_information_schedule)

    def init_calculation_service(self, energy_system: esdl.EnergySystem):
        LOGGER.info("init calculation service")
        # set windowsizes for different calculations
        self.window_size = 48
        self.window_size_up_to_next_day = 144

        for esdl_id in self.simulator_configuration.esdl_ids:
            LOGGER.info(f"Example of iterating over esdl ids: {esdl_id}")
            # set in setup
            self.solar_irradiances: dict[esdl_id, list] = {}
            self.air_temperatures:  dict[esdl_id, list] = {}
            self.soil_temperatures: dict[esdl_id, list] = {}

            # Get profiles from the ESDL
            for obj in energy_system.eAllContents():
                if hasattr(obj, "id") and obj.id == esdl_id:
                    environmental_profiles = obj

            solar_irradiance_profile = environmental_profiles.solarIrradianceProfile
            air_temperature_profile  = environmental_profiles.outsideTemperatureProfile
            soil_temperature_profile = environmental_profiles.soilTemperatureProfile

            self.solar_irradiances[esdl_id] = [element.value for element in solar_irradiance_profile.element]
            self.air_temperatures[esdl_id]  = [element.value for element in air_temperature_profile.element]
            self.soil_temperatures[esdl_id] = [element.value for element in soil_temperature_profile.element]

    def weather_prediction(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        LOGGER.info("calculation 'weather_prediction' started")
        time_step_nr = time_step_number.current_time_step_number
        predicted_solar_irradiances = self.solar_irradiances[esdl_id][
                                      time_step_nr - 1:time_step_nr - 1 + self.window_size]
        predicted_air_temperatures = self.air_temperatures[esdl_id][
                                     time_step_nr - 1:time_step_nr - 1 + self.window_size]
        predicted_soil_temperatures = self.soil_temperatures[esdl_id][
                                      time_step_nr - 1:time_step_nr - 1 + self.window_size]

        LOGGER.info("calculation 'weather_prediction' finished")
        # END user calc

        # return a list for all outputs:
        ret_val = {}
        ret_val["solar_irradiance"] = predicted_solar_irradiances
        ret_val["air_temperature"] = predicted_air_temperatures
        ret_val["soil_temperature"] = predicted_soil_temperatures

        print('predicted_solar_irradiances', predicted_solar_irradiances)
        print('predicted_air_temperatures', predicted_air_temperatures)
        print('predicted_soil_temperatures', predicted_soil_temperatures)

        # TODO: check and add influx entries
        # self.influx_connector.set_time_step_data_point(esdl_id, "EConnectionDispatch", simulation_time, ret_val["EConnectionDispatch"])
        return ret_val
    
    def weather_prediction_up_to_next_day(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        # START user calc
        LOGGER.info("calculation 'weather_prediction_up_to_next_day' started")
        time_step_nr = time_step_number.current_time_step_number
        hour_of_day = simulation_time.hour
        minute_of_hour = simulation_time.minute

        # Output non-empty lists at 12:00
        if hour_of_day == 12 and minute_of_hour == 0.0:
            predicted_air_temperatures = self.air_temperatures[esdl_id][
                                         time_step_nr - 1:time_step_nr - 1 + self.window_size_up_to_next_day]
            predicted_soil_temperatures = self.soil_temperatures[esdl_id][
                                          time_step_nr - 1:time_step_nr - 1 + self.window_size_up_to_next_day]
            predicted_solar_irradiances = self.solar_irradiances[esdl_id][
                                          time_step_nr - 1:time_step_nr - 1 + self.window_size_up_to_next_day]
        else:
            predicted_air_temperatures = []
            predicted_soil_temperatures = []
            predicted_solar_irradiances = []

        LOGGER.info("calculation 'weather_prediction_up_to_next_day' finished")
        # END user calc

        # return a list for all outputs:
        ret_val = {}
        ret_val["solar_irradiance_up_to_next_day"] = predicted_solar_irradiances
        ret_val["air_temperature_up_to_next_day"]  = predicted_air_temperatures
        ret_val["soil_temperature_up_to_next_day"] = predicted_soil_temperatures

        print('predicted_solar_irradiances_up_to_next_day', predicted_solar_irradiances)
        print('predicted_air_temperatures_up_to_next_day', predicted_air_temperatures)
        print('predicted_soil_temperatures_up_to_next_day', predicted_soil_temperatures)
        return ret_val

if __name__ == "__main__":

    helics_simulation_executor = CalculationServiceWeather()
    helics_simulation_executor.start_simulation()
    helics_simulation_executor.stop_simulation()
