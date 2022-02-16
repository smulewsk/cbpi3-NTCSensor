# NTCSensor

Plugin for Craftbeerpi 3 to measure temperature from NTC sensor using external ADC. The externel ADC is connected to RPi on the I2C bus.

IMPORTANT!!!! Please select jumper JP1 to the right NTC value:
* 1-2 NTC 100Kohms
* 2-3 NTC 10Kohms


## Parameter

* Offset - Offset which is added to the received sensor data. Positive and negative values are both allowed
* Rs - Value of the series resistor connected to the thermistor  (330ohms for 10k thermistor, 3.3Kohms for 100k thermistor)
* Rs connected to - Type of Rs connection (Select GND when using Brew Pi Hat)
* Vmax - Voltage max of ADC (Select 5V when using Brew Pi Hat)
* Beta - Beta of thermistor (default value 3950)
* Delay - Delay of measurement in secs (default 2 seconds)


## Parameter

Go to modules/plugins folder in your Craftbeerpi 3 installation directory and execute the following command:

git clone https://github.com/smulewsk/cbpi3-NTCSensor.git
