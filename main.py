from machine import Pin
import time

from components.display import display_text
from components.sampling import PulseSampler
from components.button import RotaryEncoder, TURN_RIGHT, TURN_LEFT, BUTTON_PRESS
from components.wifi import connect_wifi
from components.measurement import MeasurementSession
from components.kubios import KubiosClient, get_real_mac
from components.ui import show_menu, show_hrv_result, show_history, show_status, get_result_files

SCHOOL_SSID = ""
SCHOOL_PASSWORD = ""
PHONE_SSID = "iPhone (Arthur)"
PHONE_PASSWORD = "11111111"
BROKER_IP = ""

KUBIOS_REQUEST_TOPIC = "kubios/request"
KUBIOS_RESPONSE_TOPIC = "kubios/response"
MAX_HISTORY_FILES = 3

MENU_ITEMS = ["1. MEASURE", "2. LAST RESULT", "3. SEND KUBIOS", "4. HISTORY", "5. STATUS"]

led = Pin("LED", Pin.OUT)
sampler = PulseSampler(adc_pin=27, sample_hz=250, fifo_size=1024)
encoder = RotaryEncoder(clk_pin=10, dt_pin=11, sw_pin=12)

current_menu = "menu"
selected_menu = 1
history_index = 0
history_detail_open = False
wifi_ip = None
real_mac = ""
kubios = None


def get_wifi_credentials():
    if SCHOOL_SSID and SCHOOL_PASSWORD:
        return SCHOOL_SSID, SCHOOL_PASSWORD
    return PHONE_SSID, PHONE_PASSWORD


def next_prefixed_filename(prefix):
    max_id = 0
    for filename in get_result_files():
        if filename.startswith(prefix + " "):
            try:
                number = int(filename.split(prefix + " ")[1])
                if number > max_id:
                    max_id = number
            except:
                pass
    return "{} {}".format(prefix, max_id + 1)


measurement = MeasurementSession(sampler, led, next_prefixed_filename, MAX_HISTORY_FILES)


def move_selection(direction):
    global selected_menu

    selected_menu += direction
    if selected_menu < 1:
        selected_menu = len(MENU_ITEMS)
    elif selected_menu > len(MENU_ITEMS):
        selected_menu = 1


def select_current_menu():
    global current_menu, history_detail_open

    if current_menu == "menu":
        if selected_menu == 1:
            measurement.start()
            current_menu = "measurement"
        elif selected_menu == 2:
            current_menu = "hrv_result"
        elif selected_menu == 3:
            current_menu = "send_kubios"
        elif selected_menu == 4:
            current_menu = "history"
            history_detail_open = False
        elif selected_menu == 5:
            current_menu = "status"
    elif current_menu == "measurement":
        stop_measurement()
    elif current_menu == "history":
        if history_detail_open:
            history_detail_open = False
            current_menu = "menu"
        else:
            history_detail_open = True
    else:
        current_menu = "menu"


def stop_measurement():
    global current_menu

    result = measurement.stop()
    if result == "need_30_sec":
        display_text("NEED 30 SEC", "MEASURE AGAIN", center=True)
        time.sleep(1)
        current_menu = "menu"
    elif result == "not_enough_data":
        display_text("NOT ENOUGH", "DATA", center=True)
        time.sleep(1)
        current_menu = "menu"
    else:
        current_menu = "hrv_result"


def handle_encoder_events():
    global history_index

    event = encoder.read_event()
    while event is not None:
        if current_menu == "menu":
            if event == TURN_RIGHT:
                move_selection(1)
            elif event == TURN_LEFT:
                move_selection(-1)
        elif current_menu == "history" and not history_detail_open:
            files = get_result_files()
            if files and event == TURN_RIGHT:
                history_index = (history_index + 1) % len(files)
            elif files and event == TURN_LEFT:
                history_index = (history_index - 1) % len(files)

        if event == BUTTON_PRESS:
            select_current_menu()
        event = encoder.read_event()


print("Start")
real_mac = get_real_mac()
ssid, password = get_wifi_credentials()

display_text("WiFi", "Connecting...", center=True)
wifi_ip = connect_wifi(ssid, password)
if wifi_ip is None:
    display_text("WiFi FAILED", "Offline mode", center=True)
else:
    display_text("WiFi OK", wifi_ip, center=True)
time.sleep_ms(800)

kubios = KubiosClient(
    BROKER_IP,
    KUBIOS_REQUEST_TOPIC,
    KUBIOS_RESPONSE_TOPIC,
    real_mac,
    MAX_HISTORY_FILES,
)

if wifi_ip is not None and BROKER_IP:
    display_text("MQTT", "Connecting...", center=True)
    if kubios.connect() == "ok":
        display_text("MQTT OK", BROKER_IP, center=True)
    else:
        display_text("MQTT FAILED", "Offline mode", center=True)
    time.sleep_ms(800)
elif wifi_ip is not None:
    display_text("MQTT OFFLINE", "No broker IP", center=True)
    time.sleep_ms(800)

display_text("PULSE SENSOR", "PRESS TO START", center=True)
time.sleep_ms(800)

while True:
    handle_encoder_events()
    kubios.check_messages()

    if current_menu == "menu":
        show_menu(MENU_ITEMS, selected_menu)
    elif current_menu == "measurement":
        measurement.process()
    elif current_menu == "hrv_result":
        show_hrv_result(measurement)
    elif current_menu == "send_kubios":
        kubios.send(
            measurement.get_last_intervals(),
            measurement.get_rec_seconds(),
            measurement.min_measurement_seconds,
            wifi_ip,
        )
        current_menu = "menu"
    elif current_menu == "history":
        history_index = show_history(history_index, history_detail_open)
    elif current_menu == "status":
        show_status(wifi_ip, kubios, BROKER_IP, real_mac, measurement.get_rec_seconds())
