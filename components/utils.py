import math
import time


def calculate_heart_metrics(beats):
    """
    Calculates key heart rate variability (HRV) metrics based on a list of heartbeat timestamps.

    Args:
        beats (list): List of heartbeat timestamps in milliseconds.

    Returns:
        tuple:
            - float or None: Mean PPI (Peak-to-Peak Interval) in ms.
            - float or None: Mean Heart Rate (BPM).
            - float or None: SDNN (Standard Deviation of NN intervals).
            - float or None: RMSSD (Root Mean Square of Successive Differences).

    Note:
        - The input must contain at least 2 timestamps.
        - If data is insufficient, returns (None, None, None, None).
    """
    if len(beats) < 2:
        return None, None, None, None  # Not enough data to compute metrics

    # Calculate intervals between successive beats (PPIs)
    ppi = [
        time.ticks_diff(beats[i], beats[i - 1])
        for i in range(1, len(beats))
        if time.ticks_diff(beats[i], beats[i - 1]) <= 3000
    ]

    if not ppi:
        return None, None, None, None

    # Mean PPI
    mean_ppi = sum(ppi) / len(ppi)

    # Mean Heart Rate (HR = 60000 ms per minute / mean PPI)
    mean_hr = 60000 / mean_ppi if mean_ppi else None

    # Standard deviation of NN intervals (SDNN)
    variance = sum((x - mean_ppi) ** 2 for x in ppi) / len(ppi)
    sdnn = math.sqrt(variance)

    # Root Mean Square of Successive Differences (RMSSD)
    if len(ppi) < 2:
        rmssd = 0
    else:
        rmssd = math.sqrt(
            sum((ppi[i] - ppi[i - 1]) ** 2 for i in range(1, len(ppi))) / (len(ppi) - 1)
        )

    return mean_ppi, mean_hr, sdnn, rmssd


def calculate_bpm(beats):
    """
    Calculates the number of valid heartbeats (BPM estimate),
    filters timestamps older than 60 seconds,
    and removes intervals longer than 2000 ms (to exclude noise or missed beats).

    Args:
        beats (list): List of heartbeat timestamps in milliseconds.

    Returns:
        tuple:
            - int: Number of valid beats within the last 60 seconds and with reasonable intervals.
            - list: Filtered list of beat timestamps.
            - list: List of intervals (in ms) between consecutive valid beats.
    """
    current_time = time.ticks_ms()

    # Keep only beats from the last 60 seconds
    beats = [t for t in beats if time.ticks_diff(current_time, t) <= 60000]

    # Recalculate intervals and keep realistic pulse intervals.
    valid_beats = beats[:1]
    intervals = []  # [800, 850, ...]
    for i in range(1, len(beats)):
        interval = time.ticks_diff(beats[i], beats[i - 1])
        if 300 <= interval <= 2000:
            intervals.append(interval)
            valid_beats.append(beats[i])
    bpm = int(60000 / (sum(intervals)/len(intervals))) if len(intervals) > 1 else 0
    return bpm, valid_beats, intervals  # bpm, timestamps, intervals


def format_timestamp(timestamp_str):
    """
    Converts a timestamp string like '2025-04-17T11:00:59.823254+00:00'
    into the format '17.4.2025 11:00'.
    """
    try:
        # Split the timestamp into date and time parts
        date_part, time_part = timestamp_str.split("T")
        year, month, day = date_part.split("-")

        # Split time and take only hours and minutes
        hour, minute, *_ = time_part.split(":")
        minute = minute[:2]  # remove microseconds and timezone

        # Return formatted string in 'day.month.year hour:minute' format
        return "{}.{}.{} {}:{}".format(int(day), int(month), year, hour, minute)
    except Exception as e:
        # Return fallback string if parsing fails
        return "Invalid timestamp"
