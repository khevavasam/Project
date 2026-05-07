import time
import machine

from components.display import display_text, display_graph
from components.history import save_file, trim_history
from components.utils import calculate_heart_metrics, calculate_bpm


class MeasurementSession:
    def __init__(self, sampler, led, next_filename, max_history_files):
        self.sampler = sampler
        self.led = led
        self.next_filename = next_filename
        self.max_history_files = max_history_files

        self.max_samples = 128
        self.short_average = 3
        self.long_average = 100
        self.beat_threshold = 100
        self.min_finger_range = 250
        self.max_finger_range = 12000
        self.min_finger_average = 5000
        self.debug_interval_ms = 1000
        self.min_measurement_seconds = 30

        self.last_saved_result = None
        self.start()

    def start(self):
        self.history = []
        self.smooth_history = []
        self.beats = []
        self.beat_active = False
        self.finger_is_present = False
        self.bpm = 0
        self.last_bpm_update = time.ticks_ms()
        self.last_display_update = time.ticks_ms()
        self.last_debug_print = time.ticks_ms()
        self.valid_measurement_start = None
        self.rec_seconds = 0
        self.last_intervals = []
        self.led.value(0)

    def get_last_result(self):
        return self.last_saved_result

    def get_last_intervals(self):
        return self.last_intervals

    def get_rec_seconds(self):
        return self.rec_seconds

    def has_valid_measurement(self):
        return self.rec_seconds >= self.min_measurement_seconds

    def reset_no_finger_state(self):
        self.beats = []
        self.beat_active = False
        self.bpm = 0
        self.last_intervals = []
        self.valid_measurement_start = None
        self.rec_seconds = 0
        self.led.value(0)

    def get_signal_stats(self):
        recent = self.history[-self.long_average:]
        min_value = min(recent)
        max_value = max(recent)
        avg_value = sum(recent) / len(recent)
        signal_range = max_value - min_value
        return min_value, max_value, signal_range, avg_value

    def is_finger_detected(self):
        if len(self.history) < self.long_average:
            return False

        min_value, max_value, signal_range, avg_value = self.get_signal_stats()
        return (
            signal_range >= self.min_finger_range
            and signal_range <= self.max_finger_range
            and avg_value >= self.min_finger_average
        )

    def print_signal_debug(self):
        now = time.ticks_ms()
        if len(self.history) < self.long_average:
            return
        if time.ticks_diff(now, self.last_debug_print) < self.debug_interval_ms:
            return

        min_value, max_value, signal_range, avg_value = self.get_signal_stats()
        print(
            "signal min={} max={} range={} avg={} finger={}".format(
                int(min_value),
                int(max_value),
                int(signal_range),
                int(avg_value),
                self.finger_is_present,
            )
        )
        self.last_debug_print = now

    def detect_heartbeat(self):
        avg_short = sum(self.history[-self.short_average:]) / self.short_average
        avg_long = sum(self.history[-self.long_average:]) / self.long_average
        self.smooth_history.append(avg_short)

        if avg_short - avg_long > self.beat_threshold:
            if not self.beat_active:
                self.led.value(1)
                self.beats.append(time.ticks_ms())
                self.beat_active = True
        else:
            self.led.value(0)
            self.beat_active = False

    def process(self):
        try:
            value = self.sampler.read()
            if value is None:
                time.sleep_ms(2)
                return

            self.history.append(value)
            self.history = self.history[-self.max_samples:]
            self.smooth_history = self.smooth_history[-self.max_samples:]

            self.finger_is_present = self.is_finger_detected()
            self.print_signal_debug()

            if self.finger_is_present:
                if self.valid_measurement_start is None:
                    self.valid_measurement_start = time.ticks_ms()
                    self.rec_seconds = 0
                self.detect_heartbeat()
            else:
                self.reset_no_finger_state()

            now = time.ticks_ms()
            if self.finger_is_present and self.valid_measurement_start is not None:
                self.rec_seconds = time.ticks_diff(now, self.valid_measurement_start) // 1000

            if self.finger_is_present and time.ticks_diff(now, self.last_bpm_update) >= 5000:
                self.bpm, self.beats, self.last_intervals = calculate_bpm(self.beats)
                self.last_bpm_update = now

            if time.ticks_diff(now, self.last_display_update) >= 50:
                if self.finger_is_present:
                    display_graph(self.history, self.bpm, self.rec_seconds)
                else:
                    display_text("PLACE FINGER", "NO SIGNAL", "REC 0s", center=True)
                self.last_display_update = now

        except OSError:
            machine.reset()

    def create_result(self):
        if not self.has_valid_measurement():
            return None

        mean_ppi, mean_hr, sdnn, rmssd = calculate_heart_metrics(self.beats)
        if mean_ppi is None:
            return None

        bpm, _beats, intervals = calculate_bpm(self.beats)
        self.last_intervals = intervals
        return {
            "timestamp_ms": time.ticks_ms(),
            "bpm": bpm if bpm > 0 else self.bpm,
            "mean_ppi": int(mean_ppi),
            "mean_hr": int(mean_hr),
            "sdnn": int(sdnn),
            "rmssd": int(rmssd),
            "intervals": intervals,
        }

    def stop(self):
        self.led.value(0)
        if not self.has_valid_measurement():
            return "need_30_sec"

        result = self.create_result()
        if result is None:
            return "not_enough_data"

        save_file(self.next_filename("HRV"), result)
        trim_history(self.max_history_files)
        self.last_saved_result = result
        return "ok"
