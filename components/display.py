from machine import Pin, I2C
import ssd1306

# Setting up I2C
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


# Function to display the header
def display_title(title):
    oled.fill_rect(0, 0, 128, 10, 0)
    oled.text(title, 0, 0)
    oled.hline(0, 10, 128, 1)
    oled.show()


def display_text(line1=None, line2=None, line3=None, line4=None, line5=None, line6=None, center=False):
    lines = {
        1: {"y": 0, "text": str(line1) if line1 is not None else ""},
        2: {"y": 10, "text": str(line2) if line2 is not None else ""},
        3: {"y": 20, "text": str(line3) if line3 is not None else ""},
        4: {"y": 30, "text": str(line4) if line4 is not None else ""},
        5: {"y": 40, "text": str(line5) if line5 is not None else ""},
        6: {"y": 50, "text": str(line6) if line6 is not None else ""},
    }

    for line_num, data in lines.items():
        y = data["y"]
        text = data["text"]

        oled.fill_rect(0, y, 128, 10, 0)  # Cleaning the line
        if text:
            if center:
                x = (128 - len(text) * 8) // 2
            else:
                x = 0
            oled.text(text, x, y)

    oled.show()


def display_clear():
    oled.fill(0)
    oled.show()


# Using functions
# display_title(oled, "Header")
# display_text(oled, "Text 1", "Text 2", "Text 3", "Text 4")

# Data normalization function
def normalize(value, min_value, max_value, height):
    if min_value == max_value:  # If the values are the same, set a fixed range
        return height // 2
    return height - int((value - min_value) / (max_value - min_value) * height)


# Function for displaying graph
def display_graph(history, bpm, seconds=None):
    oled.fill(0)
    if len(history) < 2:
        oled.show()
        return

    min_val = min(history) if history else 0
    max_val = max(history) if history else 1

    # Limit the length of the history list to draw only the last 128 values
    history_to_display = history[-128:]

    # Draw the number of beats at the top
    if bpm > 0:
        oled.text(f"BPM: {bpm}", 0, 0)
    else:
        oled.text(f"Calibration...", 0, 0)
    if seconds is not None:
        oled.text("REC {:02d}s".format(seconds), 72, 0)

    # Looping through points and drawing lines between them
    for x in range(1, len(history_to_display)):
        prev_value = history_to_display[x - 1]
        current_value = history_to_display[x]
        prev_y = normalize(prev_value, min_val, max_val, 44)
        current_y = normalize(current_value, min_val, max_val, 44)

        oled.line(x - 1, prev_y + 10, x, current_y + 10, 1)

    oled.show()


def draw_progress_bar(progress, max_value):
    """Draws a progress bar with a 120px wide and text '43% / 100% 'above it."""
    bar_x = 4
    bar_y = 60
    bar_width = 120
    bar_height = 3

    if max_value <= 0:
        max_value = 1
    if progress < 0:
        progress = 0
    if progress > max_value:
        progress = max_value

    fill_width = int((progress / max_value) * bar_width)

    oled.fill_rect(bar_x, bar_y, bar_width, bar_height, 0)

    oled.rect(bar_x, bar_y, bar_width, bar_height, 1)
    oled.fill_rect(bar_x + 1, bar_y + 1, fill_width, bar_height - 2, 1)

    oled.show()
