import network
import time


def connect_wifi(ssid, password, timeout_s=15):
    if not ssid:
        print("Wi-Fi SSID is empty")
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        wlan.disconnect()
    except:
        pass

    try:
        # Disable Wi-Fi power saving on Pico W if supported by the firmware.
        wlan.config(pm=0xA11140)
    except:
        pass

    print("Connecting to Wi-Fi:", ssid)
    wlan.connect(ssid, password)

    elapsed = 0
    while not wlan.isconnected() and elapsed < timeout_s:
        print("Wi-Fi status:", wlan.status())
        time.sleep(1)
        elapsed += 1

    if not wlan.isconnected():
        print("Wi-Fi connection failed:", ssid, "status:", wlan.status())
        return None

    ip = wlan.ifconfig()[0]
    print("Connected to Wi-Fi:", ssid, ip)
    return ip
