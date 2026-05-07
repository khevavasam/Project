from machine import ADC
from fifo import Fifo
from piotimer import Piotimer


class PulseSampler:
    def __init__(self, adc_pin=27, sample_hz=250, fifo_size=1024):
        self._adc = ADC(adc_pin)
        self.fifo = Fifo(fifo_size)
        self._timer = Piotimer(freq=sample_hz, mode=Piotimer.PERIODIC, callback=self._sample_callback)

    def _sample_callback(self, _timer):
        # ISR must stay minimal: read ADC and push to FIFO.
        try:
            self.fifo.put(self._adc.read_u16())
        except RuntimeError:
            pass

    def read(self):
        if self.fifo.has_data():
            return self.fifo.get()
        return None

    def has_data(self):
        return self.fifo.has_data()

    def clear(self):
        while self.has_data():
            self.read()

    def deinit(self):
        self._timer.deinit()
