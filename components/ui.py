from components.display import display_text
from components.history import list_files, open_file


def show_menu(menu_items, selected_menu):
    items = menu_items[:]
    items[selected_menu - 1] = ">" + items[selected_menu - 1]
    display_text(*items)


def show_hrv_result(measurement):
    result = measurement.create_result()
    if result is None:
        result = measurement.get_last_result()

    if result is None:
        display_text("NO RESULT", "MEASURE FIRST", center=True)
        return

    display_text(
        "LAST HRV",
        "BPM: {}".format(result["bpm"]),
        "PPI: {}".format(result["mean_ppi"]),
        "SDNN: {}".format(result["sdnn"]),
        "RMSSD: {}".format(result["rmssd"]),
    )


def get_result_files():
    return [
        filename
        for filename in list_files()
        if filename.startswith("HRV ") or filename.startswith("KUBIOS ")
    ]


def show_result_detail(filename, result):
    if filename.startswith("KUBIOS "):
        try:
            analysis = result["data"]["analysis"]
            display_text(
                "KUBIOS",
                "HR: {}".format(int(analysis["mean_hr_bpm"])),
                "PPI: {}".format(analysis["mean_rr_ms"]),
                "SDNN: {}".format(int(analysis["sdnn_ms"])),
                "RMSSD: {}".format(int(analysis["rmssd_ms"])),
                "SNS:{} PNS:{}".format(round(analysis["sns_index"], 2), round(analysis["pns_index"], 2)),
            )
        except Exception as e:
            print("Bad Kubios history:", e)
            display_text("KUBIOS", "BAD RESPONSE", center=True)
        return

    display_text(
        "HRV",
        "BPM: {}".format(result["bpm"]),
        "PPI: {}".format(result["mean_ppi"]),
        "SDNN: {}".format(result["sdnn"]),
        "RMSSD: {}".format(result["rmssd"]),
    )


def show_history(history_index, detail_open):
    files = get_result_files()
    if not files:
        display_text("NO HISTORY", "MEASURE FIRST", center=True)
        return 0

    if history_index >= len(files):
        history_index = len(files) - 1
    if history_index < 0:
        history_index = 0

    selected_file = files[history_index]
    if detail_open:
        show_result_detail(selected_file, open_file(selected_file))
        return history_index

    lines = []
    for i in range(len(files)):
        prefix = ">" if i == history_index else " "
        lines.append(prefix + files[i])
    display_text(*lines)
    return history_index


def show_status(wifi_ip, kubios_client, broker_ip, real_mac, rec_seconds):
    display_text(
        "WiFi: " + ("OK" if wifi_ip else "OFF"),
        "MQTT: " + ("OK" if kubios_client.is_connected() else "OFF"),
        "B:" + (broker_ip if broker_ip else "OFF"),
        "MAC:" + real_mac,
        "Last: {}s".format(rec_seconds),
        "Records: {}".format(len(get_result_files())),
    )
