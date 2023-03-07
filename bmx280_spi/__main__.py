'''
Usage:
======

$ python3 -m bmx280_spi --help
usage: __main__.py [-h] [--gpio-chip GPIO_CHIP] [--time TIME] [--interval INTERVAL] [--spi SPI_BUS] [--spi-freq SPI_FREQ] [--temp-f] [--pressure PRES_FORMAT] gpio

Start a bme280/bmp280 test run using the bmx_spi library or the default RPi based library. Exact model is polled from the SPI device.

positional arguments:
  gpio                  GPIO to use for signaling the DHT sensor. If using GPIO_CHIP other than 0, set the "--gpio-chip x" option.

optional arguments:
  -h, --help            show this help message and exit
  --gpio-chip GPIO_CHIP
                        (default 0) GPIO chip for the GPIO provided. (0 typical for Pi4)
  --time TIME           (default 120) Time in seconds to run the test
  --interval INTERVAL   (default 1) Interval between reads. 1sec min for DHT11, 2sec min for DHT22 (per spec)
  --spi SPI_BUS         (default 0) SPI Bus number to use (assumes kernel driver loaded and accessible by spidev)
  --spi-freq SPI_FREQ   (default 500000Hz) Frequence to run on the SPI Bus.
  --temp-f              (default False) Print temps in F rather than C
  --pressure PRES_FORMAT
                        (default psi) Prints the pressure reading in psi|bar|pa
(venv) pi@rpi-kvm1:~/dev/bmx280_spi $ python3 -m bmx280_spi --spi 1 13 --time 10 --pressure psi --temp-f

BME280:
2023-03-03 23:10:15,263 - root - INFO - 10/10 (100.0%): Temps (min/avg/max): 75.74/75.77/75.79 deg F, Humidity (min/avg/max): 24.94/24.95/24.98 %, Pressure (min/avg/max): 14.05/14.06/14.06 psi

BMP280:



MIT License

Copyright (c) 2022 LearningToPi <contact@learningtopi.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import argparse
from time import time, sleep
from . import Bmx280Spi, Bmx280Readings, MODE_NORMAL
from logging_handler import create_logger, INFO, DEBUG

DEF_GPIO_CHIP = 0
DEF_TIME = 120
DEF_INTERVAL = 1
DEF_SPI_BUS = 0
DEF_SPI_FREQ = 500_000
DEF_TEMP_F = False
DEF_PRES_FORMAT = 'psi'


def run_test(**kwargs):
    ''' Initiate the test using the provided arguments '''
    logger = create_logger(DEBUG if kwargs.get('debug', False) else INFO)

    # initiate the sensor
    sensor = Bmx280Spi(spiBus=kwargs.get('spi_bus', DEF_SPI_BUS),
            cs_pin=kwargs.get('gpio'),
            cs_chip=kwargs.get('gpio_chip', DEF_GPIO_CHIP),
            logger=logger
        )

    # Run the test!
    data = []
    count = 0
    success = 0
    logger.info(f"Starting test.  Will run for {kwargs.get('time', DEF_TIME)} seconds")
    stop_time = time() + kwargs.get('time', DEF_TIME)
    try:
        while time() < stop_time:
            count += 1
            reading = sensor.update_readings()
            if reading is not None:
                success += 1
                logger.info(reading)
                data.append(reading)
            else:
                logger.warning('Failed reading!')
            if time() + kwargs.get('interval', DEF_INTERVAL) < stop_time:
                sleep(kwargs.get('interval', DEF_INTERVAL))
            else:
                break
    except KeyboardInterrupt:
        print('Keyboard interrupt!')
    
    # calculate the min, avg and max
    if len(data) == 0 or success == 0:
        logger.error(f'No successful reads out of {count} attempts!')
        return
    temp_min = round(min([read.temp_f if kwargs.get('temp_f', DEF_TEMP_F) else read.temp_c for read in data]), 2) 
    temp_max = round(max([read.temp_f if kwargs.get('temp_f', DEF_TEMP_F) else read.temp_c for read in data]), 2) 
    temp_avg = round(sum([read.temp_f if kwargs.get('temp_f', DEF_TEMP_F) else read.temp_c for read in data]) / success, 2)
    if sensor.model == 'BME280':
        humid_min = round(min([read.humidity for read in data]), 2) 
        humid_max = round(max([read.humidity for read in data]), 2) 
        humid_avg = round(sum([read.humidity for read in data]) / success, 2)
    if kwargs.get('pres_format', DEF_PRES_FORMAT).lower() == 'pa':
        press_min = round(min([read.pressure_pa for read in data]), 2) 
        press_max = round(max([read.pressure_pa for read in data]), 2) 
        press_avg = round(sum([read.pressure_pa for read in data]) / success, 2)
        press_text = 'Pa'
    elif kwargs.get('pres_format', DEF_PRES_FORMAT).lower() == 'atm':
        press_min = round(min([read.pressure_atm for read in data]), 2) 
        press_max = round(max([read.pressure_atm for read in data]), 2) 
        press_avg = round(sum([read.pressure_atm for read in data]) / success, 2) 
        press_text = 'atm'
    else:
        press_min = round(min([read.pressure_psi for read in data]), 2)
        press_max = round(max([read.pressure_psi for read in data]), 2)
        press_avg = round(sum([read.pressure_psi for read in data]) / success, 2)
        press_text = 'psi'

    logger.info(f"{success}/{count} ({round(success/count, 4) * 100}%): Temps (min/avg/max): {temp_min}/{temp_avg}/{temp_max} deg {'F' if kwargs.get('temp_f', DEF_TEMP_F) else 'C'}, " \
            + (f"Humidity (min/avg/max): {humid_min}/{humid_avg}/{humid_max} %, " if sensor.model == 'BME280' else '') \
            + f"Pressure (min/avg/max): {press_min}/{press_avg}/{press_max} {press_text}")


if __name__ == '__main__':
    # setup the argument parser
    parser = argparse.ArgumentParser(description="Start a bme280/bmp280 test run using the bmx_spi library or the default RPi based library.  Exact model is polled from the SPI device.")
    parser.add_argument('gpio', metavar='gpio', type=int, help='GPIO to use for signaling the DHT sensor. If using GPIO_CHIP other than 0, set the "--gpio-chip x" option. ')
    parser.add_argument('--gpio-chip', dest='gpio_chip', required=False, type=int, default=DEF_GPIO_CHIP, help=f'(default {DEF_GPIO_CHIP}) GPIO chip for the GPIO provided. (0 typical for Pi4)')
    parser.add_argument('--time', dest='time', required=False, type=int, default=DEF_TIME, help=f"(default {DEF_TIME}) Time in seconds to run the test")
    parser.add_argument('--interval', dest='interval', required=False, type=int, default=DEF_INTERVAL, help=f"(default {DEF_INTERVAL}) Interval between reads.  1sec min for DHT11, 2sec min for DHT22 (per spec)")
    parser.add_argument('--spi', dest='spi_bus', required=False, type=int, default=DEF_SPI_BUS, help=f"(default {DEF_SPI_BUS}) SPI Bus number to use (assumes kernel driver loaded and accessible by spidev)")
    parser.add_argument('--spi-freq', dest='spi_freq', required=False, type=int, default=DEF_SPI_FREQ, help=f"(default {DEF_SPI_FREQ}Hz) Frequence to run on the SPI Bus.")
    parser.add_argument("--temp-f", dest='temp_f', required=False, action='store_true', default=DEF_TEMP_F, help=f"(default {DEF_TEMP_F}) Print temps in F rather than C")
    parser.add_argument("--pressure", dest='pres_format', required=False, type=str, default=DEF_PRES_FORMAT, help=f"(default {DEF_PRES_FORMAT}) Prints the pressure reading in psi|bar|pa")
    parser.add_argument("--debug", dest='debug', required=False, action='store_true', default=False, help="(default False) Enables debug logging")
    run_test(**vars(parser.parse_args()))