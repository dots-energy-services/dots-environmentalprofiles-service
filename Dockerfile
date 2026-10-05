FROM python:3.14

RUN mkdir /app/
WORKDIR /app

COPY src/WeatherService ./src/WeatherService
COPY pyproject.toml ./
COPY README.md ./

RUN pip install ./ --extra-index-url https://test.pypi.org/simple/
ENTRYPOINT ["python3", "src/WeatherService/weatherservice.py"]
