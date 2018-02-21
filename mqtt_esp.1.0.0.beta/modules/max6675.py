import machine

NUM_SPI = 1   # HSPI--1,  SPI--0

class MAX6675(object):

    def __init__(self, cs_pin=15, clk_freq=430000):
        self._address = NUM_SPI
        self._cs = machine.Pin(cs_pin, machine.Pin.OUT)
        self._bus = machine.SPI(self._address, baudrate=clk_freq, polarity=0, phase=0)
        self._cs.value(1)

    def read_data(self):
        # Read 16 bits from the SPI bus.
        self._cs.value(0)
        raw = self._bus.read(2)
        self._cs.value(1)
        if raw is None or len(raw) != 2:
            raise RuntimeError('Did not read expected number of bytes from MAX6675!')
        value = raw[0] << 8 | raw[1]
        return value

    def readTempC(self):
        """Return the thermocouple temperature value in degrees celsius."""
        v = self.read_data()
        # Check for error reading value.
        if v & 0x4:
            return float('NaN')
        # Check if signed bit is set.
        if v & 0x80000000:
            # Negative value, take 2's compliment. Compute this with subtraction
            # because python is a little odd about handling signed/unsigned.
            v >>= 3 # only need the 12 MSB
            v -= 4096
        else:
            # Positive value, just shift the bits to get the value.
            v >>= 3 # only need the 12 MSB
        # Scale by 0.25 degrees C per bit and return value.
        return v * 0.25

    def measure(self):
        t_celsius = self.readTempC()
        return t_celsius