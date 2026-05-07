from machine import Pin
import time

from fifo import Fifo

TURN_RIGHT = 1
TURN_LEFT = 2
BUTTON_PRESS = 3


class RotaryEncoder:
    def __init__(self, clk_pin=10, dt_pin=11, sw_pin=12, fifo_size=32):
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        self.events = Fifo(fifo_size)
        self.last_button_ms = 0
        self.last_turn_ms = 0

        self.clk.irq(trigger=Pin.IRQ_FALLING, handler=self._rotation_handler)
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self._button_handler)

    def _rotation_handler(self, _pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_turn_ms) > 150:
            if self.dt.value() == 1:
                self.events.put(TURN_RIGHT)
            else:
                self.events.put(TURN_LEFT)
            self.last_turn_ms = now

    def _button_handler(self, _pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_button_ms) > 250:
            self.events.put(BUTTON_PRESS)
            self.last_button_ms = now

    def read_event(self):
        if self.events.has_data():
            return self.events.get()
        return None
