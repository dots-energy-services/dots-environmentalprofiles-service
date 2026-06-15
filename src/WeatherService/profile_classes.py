from datetime import datetime, timedelta
import math

from dots_infrastructure.DataClasses import EsdlId
from esdl import DateTimeProfile, StaticProfile, TimeSeriesProfile
import pandas as pd

class ParsedStaticProfile:

    def __init__(self, data : StaticProfile):
        self._parsed_profile = self._parse_profile(data)
        self.min_date : datetime = datetime.min
        self.max_date : datetime = datetime.max
    
    def _parse_profile(self, profile):
        # Needs to be implemented by child classes
        pass

    def get_data(self, from_data : datetime, to_data : datetime):
        # Needs to be implemented by child classes
        pass

    def get_from_to_dates_in_data(self, from_data : datetime, to_data : datetime) -> tuple[datetime, datetime]:
        if self.min_date <= from_data <= self.max_date and self.min_date <= to_data <= self.max_date:
            return from_data, to_data

        delta_t_data : timedelta = to_data - from_data

        from_data_in_data = datetime(self.min_date.year, from_data.month, from_data.day, from_data.hour, from_data.minute, from_data.second, tzinfo=from_data.tzinfo)
        to_date_in_data = from_data_in_data + delta_t_data

        # Try to find first ranged contained within the data
        year = self.min_date.year
        while not (self.min_date <= from_data_in_data <= self.max_date and self.min_date <= to_date_in_data <= self.max_date):
            year += 1
            from_data_in_data = datetime(year, from_data.month, from_data.day, from_data.hour, from_data.minute, from_data.second, tzinfo=from_data.tzinfo)
            to_date_in_data = from_data_in_data + delta_t_data

        return from_data_in_data, to_date_in_data

class ParsedDateTimeProfile(ParsedStaticProfile):

    def __init__(self, data):
        super().__init__(data)
        parsed_profile : pd.DataFrame = self._parsed_profile
        self.min_date = parsed_profile.index.min()
        self.max_date = parsed_profile.index.max()

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
        from_data_in_data, to_data_in_data = self.get_from_to_dates_in_data(from_data, to_data)
        data : pd.DataFrame = self._parsed_profile
        return data[from_data_in_data:to_data_in_data]["value"].tolist()

class ParsedTimeSeriesProfile(ParsedStaticProfile):

    def __init__(self, data):
        super().__init__(data)
        parsed_profile : TimeSeriesProfile = self._parsed_profile
        self.min_date : datetime = parsed_profile.startDateTime
        self.max_date : datetime = parsed_profile.startDateTime + timedelta(seconds=len(parsed_profile.values) * parsed_profile.timestep)

    def _parse_profile(self, profile : TimeSeriesProfile):
        return profile

    def get_data(self, from_data : datetime, to_data : datetime):
        data : TimeSeriesProfile = self._parsed_profile

        from_data_in_data, to_data_in_data = self.get_from_to_dates_in_data(from_data, to_data)

        delta_t_from : timedelta = from_data_in_data - data.startDateTime
        delta_t_to : timedelta = to_data_in_data - data.startDateTime

        from_index = math.floor(delta_t_from.seconds / data.timestep)
        to_index = math.ceil(delta_t_to.seconds / data.timestep)

        return data.values[from_index:to_index]