import RPi.GPIO as GPIO
import thermometer.dht11 as dht11
from datetime import datetime
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
DHT11_instance = dht11.DHT11(pin = 4)

MIN_REFRESH_TIME_LAPSE_IN_SECONDS = 10

class Thermometer:

    temperature = None
    humidity = None
    temperature_last_update = None

    def get_temperature(self):
        self.refresh_temperature()
        return self.temperature

    #
    # Refresh inventory warehouse temperature data
    #
    def refresh_temperature(self):
        if self.temperature_last_update is not None:
            diff = datetime.now() - self.temperature_last_update
            if diff.seconds < MIN_REFRESH_TIME_LAPSE_IN_SECONDS:
                return
        result = None
        while result is None or not result.is_valid():
            result = DHT11_instance.read()
            if result.is_valid():
                self.temperature = result.temperature
                self.humidity = result.humidity
                self.temperature_last_update = datetime.now()
            else:
                time.sleep(0.5)
        GPIO.cleanup()
