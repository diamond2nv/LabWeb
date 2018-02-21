import machine
import ubinascii

NUM_SPI = 1   # HSPI--1,  SPI--0

class MAX31855(object):

    def __init__(self, cs_pin=15, clk_freq=500000):
        self._address = NUM_SPI
        self._cs = machine.Pin(cs_pin, machine.Pin.OUT)
        self._bus = machine.SPI(self._address, baudrate=clk_freq, polarity=0, phase=0)
        self._cs.value(1)

    def read_data(self):
        self._cs.value(0)
        # Read 32 bits from the SPI bus.
        data = self._bus.read(4)
        self._cs.value(1)
        ubinascii.hexlify(data)
        return data

    def get_temperature(self):
        data = self.read_data()
        temp = data[0] << 8 | data[1]
        if temp & 0x0001:
            return float('NaN')  # Fault reading data.
        temp >>= 2
        if temp & 0x2000:
            temp -= 16384  # Sign bit set, take 2's compliment.
        return temp * 0.25

    def measure(self):
        data = self.read_data()
        t_celsius = self.get_temperature(data)
        return t_celsius