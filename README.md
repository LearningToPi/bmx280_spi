# BMP280 / BME280 over SPI

Homepage: https://www.learningtopi.com/python-modules-applications/bmx280_spi/

BMP280/BME280 python3 driver using the SPI bus to control and read data.

General GPIO Pin (NOT an SPI CS) used to pull the signal pin low.  The SPI CS pins do not operate properly with the SPI kernel driver.

BMP280 datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf

BME280 datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf

BMP280/BME280 Pinout:
    SCL = SCK (SPI Clock)
    SDO = MISO (sensor out to board in)
    SDA = MOSI (sensir in to board out)
    CSB = CS (select)

### Parts:
- BMP280 (Temp and pressure) - https://amzn.to/3YVwblE
- BME280 (Temp, pressure and humidity) - https://amzn.to/3JIxtMr

## Usage:


    # Import bmx280 SPI class
    from bmx280_spi import Bmx280Spi, MODE_NORMAL

    # initialize device
    # cs_chip and cs_pin from "gpioinfo".  gpiod used for platform compatibility.
    bmx = Bmx280Spi(spiBus=0, cs_chip=0, cs_pin=26)
    bmx.set_power_mode(MODE_NORMAL)
    bmx.set_sleep_duration_value(3)
    bmx.set_temp_oversample(1)
    bmx.set_pressure_oversample(1)
    bmx.set_filter(0)
    reading = bmx.update_reading() # returns instance of Bmx280Readings
    print(reading)
    # --or--
    print(reading.temp_c, reading.temp_f, reading.pressure_psi)

## Testing
Included in the module is a basic test script that can be executed with the following:

    python3 -m dht11_spi [gpio]

Additional test options are available for interval, run time, dht22.  Documentation is available using the "--help" option.

### Example Output

    DHT11: 105/105 (100.0%): Temps (min/avg/max): 73.54/75.2/75.34 deg FHumidity (min/avg/max): 17.0/17.0/17.0 %
    DHT22: 112/112 (100.0%): Temps (min/avg/max): 74.48/74.51/74.66 deg FHumidity (min/avg/max): 14.1/14.21/16.0 %
