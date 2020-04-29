# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE, call, check_output

from modules import cbpi, app
from modules.core.hardware import SensorPassive
import json
import os, re, threading, time
from flask import Blueprint, render_template, request
from modules.core.props import Property
from math import log

import smbus

i2c_channel = 1

MCP3421_I2C_ADDRESS = 0x68
RAW_TO_V_FACTOR = 0.000015625
MCP3421_CONFIG_BYTE = 0x1c

blueprint = Blueprint('ntc', __name__)

T0_25C = 298.15

def getSensors():
    return ["Thermistor100k","Thermistor10k"]


class myThread (threading.Thread):

    value = 0
    bus = 0

    def __init__(self, sensor_name, sleep_value):
        threading.Thread.__init__(self)
        self.value = 0
        self.bus = smbus.SMBus(i2c_channel)
        self.sensor_name = sensor_name
        self.running = True
        self.bus.write_byte(MCP3421_I2C_ADDRESS, MCP3421_CONFIG_BYTE)
        self.sleep_value = sleep_value

    def swap2Bytes(self, c):
        return (c>>8 |c<<8)&0xFFFF

    def shutdown(self):
        pass

    def stop(self):
        self.running = False

    def run(self):

        while self.running:
            try:
                app.logger.info("READ ADC")
                ## Test Mode
                if self.sensor_name is None:
                    return
                self.mcpdata = self.bus.read_i2c_block_data(MCP3421_I2C_ADDRESS, MCP3421_CONFIG_BYTE,4)
                self.value = (self.mcpdata[2] + (self.mcpdata[1] << 8) + (self.mcpdata[0] << 16)) * RAW_TO_V_FACTOR
                    
            except:
                pass

            time.sleep(self.sleep_value)



@cbpi.sensor
class NTCSensor(SensorPassive):

    sensor_name = Property.Select("Sensor", getSensors(), description="The NTC sensor type.")
    offset = Property.Number("Offset", True, 0, description="Offset which is added to the received sensor data. Positive and negative values are both allowed.")
    rs = Property.Number("Rs", True, 3300, description="Value of the series resistor connected to the thermistor.")
    rs_connection = Property.Select("Rs connected to", ["5V", "GND"], description="Type of Rs connection.")
    adcMax = Property.Number("Vmax", True, 5, description="Voltage max of ADC.")
    beta = Property.Number("Beta", True, 3950, description="Beta of thermistor.")
    delay = Property.Number("Delay", True, 1, description="Delay of measurement in secs.")

    def init(self):

        self.t = myThread(self.sensor_name, self.delay_value())

        def shutdown():
            shutdown.cb.shutdown()
        shutdown.cb = self.t

        self.t.start()

    def stop(self):
        try:
            self.t.stop()
        except:
            pass

    def read(self):
        T=0
        adcVal = self.t.value
        adcMaxVal = self.adcmax_value()
        rsVal = self.rs_value()

        if self.sensor_name == "Thermistor100k":
            r0 = 100000.0
        elif self.sensor_name == "Thermistor10k":
            r0 = 10000.0
        else:
            r0 = 100000.0

        if self.rs_connection == "GND":
            rt = rsVal * ((adcMaxVal/adcVal)-1)
        else:
            rt = rsVal / ((adcMaxVal/adcVal)-1)
        a = 1.0/T0_25C + 1.0/self.beta_value() * log(rt/r0)
        T = 1.0/a
        T = T + self.offset_value()
        if self.get_config_parameter("unit", "C") == "C":
            T = T - 273.15
        if T < 0.0:
            T = 0.0

        self.data_received(round(T, 2))

    @cbpi.try_catch(0)
    def offset_value(self):
        return float(self.offset)

    @cbpi.try_catch(0)
    def rs_value(self):
        return float(self.rs)

    @cbpi.try_catch(0)
    def adcmax_value(self):
        return float(self.adcMax)

    @cbpi.try_catch(0)
    def beta_value(self):
        return float(self.beta)

    @cbpi.try_catch(0)
    def delay_value(self):
        return float(self.delay)
            
    @classmethod
    def init_global(self):
        try:
            call(["modprobe", "i2c-dec"])
        except Exception as e:
            pass


@blueprint.route('/<int:t>', methods=['GET'])
def set_temp(t):
    global temp
    temp = t
    return ('', 204)


@cbpi.initalizer()
def init(cbpi):

    cbpi.app.register_blueprint(blueprint, url_prefix='/api/ntc')
