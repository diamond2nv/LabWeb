import machine
NUM_SPI = 1
class MAX6675(object):
    def __init__(self, cs_pin=15, clk_freq=430000):
        self._address = NUM_SPI
        self._cs = machine.Pin(cs_pin, machine.Pin.OUT)
        self._bus = machine.SPI(self._address, baudrate=clk_freq, polarity=0, phase=0)
        self._cs.value(1)
    def read_data(self):
        self._cs.value(0)
        raw = self._bus.read(2)
        self._cs.value(1)
        if raw is None or len(raw) != 2:
            raise RuntimeError('Did not read expected number of bytes from MAX6675!')
        value = raw[0] << 8 | raw[1]
        return value
    def readTempC(self):
        v = self.read_data()
        if v & 0x4:
            return float('NaN')
        if v & 0x80000000:
            v >>= 3
            v -= 4096
        else:
            v >>= 3 
        return v * 0.25
    def measure(self):
        t_celsius = self.readTempC()
        return t_celsius