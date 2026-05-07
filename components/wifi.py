import network
import time


def connect_wifi(ssid, password, timeout_s=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    elapsed = 0
    while not wlan.isconnected() and elapsed < timeout_s:
        print("Connecting to Wi-Fi...")
        time.sleep(1)
        elapsed += 1

    if not wlan.isconnected():
        print("Wi-Fi connection failed")
        return None

    ip = wlan.ifconfig()[0]
    print("Connected to Wi-Fi:", ip)
    return ip
