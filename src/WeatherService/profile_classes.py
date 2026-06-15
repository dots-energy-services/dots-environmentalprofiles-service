from datetime import datetime, timedelta
import math

from dots_infrastructure.DataClasses import EsdlId
from esdl import DateTimeProfile, StaticProfile, TimeSeriesProfile
import pandas as pd

class ParsedStaticProfile:

    def __init__(self, data : StaticProfile):
        self._parsed_profile = self._parse_profile(data)
    
    def _parse_profile(self, profile):
        # Needs to be implemented by child classes
        pass

    def get_data(self, from_data : datetime, to_data : datetime):
        # Needs to be implemented by child classes
        pass

class ParsedDateTimeProfile(ParsedStaticProfile):

    def _parse_profile(self, profile : DateTimeProfile) -> pd.DataFrame:
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

    def get_data(self, from_data : datetime, to_data : datetime):
        data : pd.DataFrame = self._parsed_profile
        return data[from_data:to_data]["value"].tolist()

class ParsedTimeSeriesProfile(ParsedStaticProfile):

    def _parse_profile(self, profile : TimeSeriesProfile):
        return profile

    def get_data(self, from_data : datetime, to_data : datetime):
        data : TimeSeriesProfile = self._parsed_profile

        delta_t_from : timedelta = from_data - data.startDateTime
        delta_t_to : timedelta = to_data - data.startDateTime

        from_index = math.floor(delta_t_from.seconds / data.timestep)
        to_index = math.ceil(delta_t_to.seconds / data.timestep)

        return data.values[from_index:to_index]