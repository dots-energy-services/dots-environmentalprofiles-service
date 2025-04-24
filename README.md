
# Calculation service for esdl_type EnvironmentalProfiles:

This calculation service publishes specified in the weather profiles of the ESDL. The values of the profiles should be specified in the ESDL file.

## Calculations

### weather prediction 

Send the values of the weather profile for the coming 12 hours.
#### Output values
|Name             |data_type             |unit             |description             |
|-----------------|----------------------|-----------------|------------------------|
|solar_irradiance|VECTOR|Wm2|The solar irradiance as vector of floats for the next 12 hours in watt per square metre|
|air_temperature|VECTOR|K|The air temperature as vector of floats for the next 12 hours in Kelvin.|
|soil_temperature|VECTOR|K|The soil temperature as vector of floats for the next 12 hours in Kelvin.|

### Relevant links
|Link             |description             |
|-----------------|------------------------|
|[Environmental Profiles](https://energytransition.github.io/#router/doc-content/687474703a2f2f7777772e746e6f2e6e6c2f6573646c/EnvironmentalProfiles.html)|Details on the EnvironmentalProfiles esdl type|
