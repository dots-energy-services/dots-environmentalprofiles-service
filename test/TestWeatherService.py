from datetime import datetime
import unittest
from WeatherService.weatherservice import CalculationServiceWeather
from dots_infrastructure.DataClasses import SimulatorConfiguration,TimeStepInformation
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
from esdl.esdl_handler import EnergySystemHandler
import helics as h

from dots_infrastructure import CalculationServiceHelperFunctions

BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960

def simulator_environment_e_connection():
    return SimulatorConfiguration("EnvironmentalProfiles", ["ebca3673-20de-42bf-b005-2a01926e4564"], "Mock-EnvironmentalProfiles", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, [])

class Test(unittest.TestCase):

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        esh = EnergySystemHandler()
        esh.load_file("test.esdl")
        self.energy_system = esh.get_energy_system()

    def test_weather_prediction(self):
        # Arrange
        service = CalculationServiceWeather()
        service.init_calculation_service(self.energy_system)

        # Execute
        ret_val = service.weather_prediction({}, datetime(2020,1,14,0,0), TimeStepInformation(1,2), "ebca3673-20de-42bf-b005-2a01926e4564", self.energy_system)
        
        # Assert
        expected_outcome_air_temperature = [285.04999999999995, 284.575, 284.1, 283.625, 283.15, 283.125, 283.1, 283.075, 283.04999999999995, 283.0, 282.95, 282.9, 282.85, 282.85, 282.85, 282.85, 282.85, 282.79999999999995, 282.75, 282.7, 282.65, 282.625, 282.6, 282.575, 282.54999999999995, 282.525, 282.5, 282.475, 282.45, 282.4, 282.35, 282.29999999999995, 282.25, 282.25, 282.25, 282.25, 282.25, 282.375, 282.5, 282.625, 282.75, 282.775, 282.79999999999995, 282.825, 282.85, 282.875, 282.9, 282.92499999999995, ]
        expected_outcome_soil_temperature = [281.15, 281.1458333333333, 281.14166666666665, 281.1375, 281.1333333333333, 281.12916666666666, 281.125, 281.12083333333334, 281.1166666666666, 281.11249999999995, 281.1083333333333, 281.10416666666663, 281.1, 281.0958333333333, 281.09166666666664, 281.0875, 281.0833333333333, 281.07916666666665, 281.075, 281.0708333333333, 281.06666666666666, 281.0625, 281.05833333333334, 281.0541666666666, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995, 281.04999999999995]
        expected_outcome_solar_irradiance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.083333333333333, 4.166666666666667, 6.25, 8.333333333333334, 15.277777777777777, 22.22222222222222, 29.166666666666664, 36.11111111111111, 44.44444444444444, 52.77777777777777, 61.11111111111111, 69.44444444444444, 68.05555555555556, 66.66666666666666, 65.27777777777779] 

        self.assertListEqual(ret_val["air_temperature"], expected_outcome_air_temperature)
        self.assertListEqual(ret_val["soil_temperature"], expected_outcome_soil_temperature)
        self.assertListEqual(ret_val["solar_irradiance"], expected_outcome_solar_irradiance)

if __name__ == '__main__':
    unittest.main()
