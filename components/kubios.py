import time
import ujson
import network
import ubinascii

from components.display import display_text
from components.history import save_file, trim_history
from components.mqtt_utils import connect_mqtt, send_mqtt_message, parse_json_message


def get_real_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ubinascii.hexlify(wlan.config("mac")).decode()


class KubiosClient:
    def __init__(self, broker_ip, request_topic, response_topic, real_mac, max_history_files):
        self.broker_ip = broker_ip
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.real_mac = real_mac
        self.max_history_files = max_history_files
        self.mqtt_client = None
        self.last_result = None
        self.response_received = False

    def connect(self):
        if not self.broker_ip:
            return "no_broker"
        try:
            self.mqtt_client = connect_mqtt(
                self.broker_ip,
                self.response_topic,
                self.callback,
                self.real_mac,
            )
            return "ok"
        except Exception as e:
            print("MQTT connection failed:", e)
            self.mqtt_client = None
            return "failed"

    def is_connected(self):
        return self.mqtt_client is not None

    def callback(self, topic, msg):
        try:
            data = parse_json_message(msg)
            if data.get("mac") != self.real_mac:
                print("Ignoring Kubios response for other mac")
                return
            save_file(self.next_filename("KUBIOS"), data)
            trim_history(self.max_history_files)
            self.last_result = data
            self.response_received = True
            print("Received Kubios response:", topic)
        except Exception as e:
            print("Failed to handle Kubios response:", e)

    def next_filename(self, prefix):
        from components.history import list_files

        max_id = 0
        for filename in list_files():
            if filename.startswith(prefix + " "):
                try:
                    number = int(filename.split(prefix + " ")[1])
                    if number > max_id:
                        max_id = number
                except:
                    pass
        return "{} {}".format(prefix, max_id + 1)

    def check_messages(self):
        if self.mqtt_client is None:
            return
        try:
            self.mqtt_client.check_msg()
        except Exception as e:
            print("MQTT check failed:", e)
            self.mqtt_client = None

    def show_result(self, data):
        try:
            analysis = data["data"]["analysis"]
            display_text(
                "KUBIOS RESULT",
                "HR: {}".format(int(analysis["mean_hr_bpm"])),
                "PPI: {}".format(analysis["mean_rr_ms"]),
                "RMSSD: {}".format(int(analysis["rmssd_ms"])),
                "SDNN: {}".format(int(analysis["sdnn_ms"])),
                "SNS:{} PNS:{}".format(round(analysis["sns_index"], 2), round(analysis["pns_index"], 2)),
            )
        except Exception as e:
            print("Bad Kubios result:", e)
            display_text("KUBIOS", "BAD RESPONSE", center=True)

    def send(self, intervals, rec_seconds, min_measurement_seconds, wifi_ip):
        if rec_seconds < min_measurement_seconds:
            display_text("NEED 30 SEC", center=True)
            time.sleep(1)
            return
        if len(intervals) < 12:
            display_text("NOT ENOUGH", "DATA", center=True)
            time.sleep(1)
            return
        if wifi_ip is None:
            display_text("KUBIOS OFFLINE", center=True)
            time.sleep(1)
            return
        if self.mqtt_client is None:
            display_text("MQTT", "OFFLINE", center=True)
            time.sleep(1)
            return

        data = {
            "mac": self.real_mac,
            "type": "RRI",
            "data": intervals,
            "analysis": {"type": "readiness"},
        }

        self.response_received = False
        display_text("SENDING", "KUBIOS...", center=True)
        if not send_mqtt_message(self.mqtt_client, self.request_topic, ujson.dumps(data)):
            display_text("MQTT SEND", "FAILED", center=True)
            time.sleep(1)
            return

        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < 5000:
            self.check_messages()
            if self.response_received:
                self.show_result(self.last_result)
                time.sleep(3)
                return
            if self.mqtt_client is None:
                display_text("MQTT", "OFFLINE", center=True)
                time.sleep(1)
                return
            time.sleep_ms(100)

        display_text("NO KUBIOS", "RESPONSE", center=True)
        time.sleep(1)
