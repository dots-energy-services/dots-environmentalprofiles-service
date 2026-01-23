FROM python:3.14

RUN mkdir /app/
WORKDIR /app

COPY src/WeatherService ./src/WeatherService
COPY pyproject.toml ./
COPY README.md ./

RUN pip install -r requirements.txt && \
    pip install ./
ENTRYPOINT ["python3", "src/WeatherService/weatherservice.py"]
