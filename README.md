# Hardware 2 Pulse & HRV Monitor

## Overview

This project is a standalone pulse and heart rate variability (HRV) monitoring system built using the Raspberry Pi Pico.

The system reads a PPG (photoplethysmography) signal through the ADC, processes the signal in real time, detects heartbeats, calculates BPM, and performs basic HRV analysis. All functionality runs directly on the Pico without requiring Thonny or a computer connection.

The device also displays information on an OLED screen, allows user interaction via a rotary encoder, and stores measurement history locally. Advanced features include Wi-Fi connectivity, MQTT communication, and integration with external HRV analysis services.

---

## Main Features

- Standalone operation (no Thonny required)
- PPG signal acquisition via ADC
- 250 Hz sampling using PIO timer and FIFO
- Real-time heartbeat detection
- BPM calculation and update
- LED indication for each detected heartbeat
- OLED display for user feedback
- Start/Stop measurement using rotary encoder
- Local HRV analysis (mean PPI, mean HR, RMSSD, SDNN)
- Measurement history stored in JSON format
- Optional Wi-Fi, MQTT, and Kubios integration

---

## System Architecture

The system follows a modular design:

PPG Sensor  
→ ADC Sampling (250 Hz)  
→ Timer Interrupt  
→ FIFO Buffer  
→ Main Loop Processing  
→ Peak Detection  
→ PPI Calculation  
→ BPM / HRV Calculation  
→ OLED Display  
→ JSON Storage  
→ (Optional) MQTT / Kubios  

---

## Project Structure

```text
main.py         - Entry point and main loop  
config.py       - System configuration and constants  
hardware.py     - ADC, OLED, LED, encoder setup  
sampling.py     - Timer, FIFO, and data acquisition  
processing.py   - Signal processing, BPM and HRV  
display.py      - OLED screens and UI  
menu.py         - User navigation and control  
storage.py      - JSON saving and history  
network.py      - Wi-Fi, MQTT, Kubios  
Goals

The main goal of this project is to design and implement a fully functional embedded system for pulse and HRV monitoring.

Key objectives:

Build a stable real-time sampling system (250 Hz)
Implement reliable heartbeat detection
Calculate realistic BPM values
Perform local HRV analysis
Store and display measurement history
Extend the system with network capabilities
Hardware
Raspberry Pi Pico
PPG sensor (analog output)
OLED display (SSD1306, I2C)
Rotary encoder (with push button)
LEDs
Project Status

Work in progress.

Current stage:

Project setup and architecture planning

Next steps:

Implement sampling pipeline (ADC + timer + FIFO)
Authors

Hardware 2 student project
Metropolia University of Applied Sciences
# Hardware 2 Pulse & HRV Monitor

## Overview

This project is a standalone pulse and heart rate variability (HRV) monitoring system built using the Raspberry Pi Pico.

The system reads a PPG (photoplethysmography) signal through the ADC, processes the signal in real time, detects heartbeats, calculates BPM, and performs basic HRV analysis. All functionality runs directly on the Pico without requiring Thonny or a computer connection.

The device also displays information on an OLED screen, allows user interaction via a rotary encoder, and stores measurement history locally. Advanced features include Wi-Fi connectivity, MQTT communication, and integration with external HRV analysis services.

---

## Main Features

- Standalone operation (no Thonny required)
- PPG signal acquisition via ADC
- 250 Hz sampling using PIO timer and FIFO
- Real-time heartbeat detection
- BPM calculation and update
- LED indication for each detected heartbeat
- OLED display for user feedback
- Start/Stop measurement using rotary encoder
- Local HRV analysis (mean PPI, mean HR, RMSSD, SDNN)
- Measurement history stored in JSON format
- Optional Wi-Fi, MQTT, and Kubios integration

---

## System Architecture

The system follows a modular design:

PPG Sensor  
→ ADC Sampling (250 Hz)  
→ Timer Interrupt  
→ FIFO Buffer  
→ Main Loop Processing  
→ Peak Detection  
→ PPI Calculation  
→ BPM / HRV Calculation  
→ OLED Display  
→ JSON Storage  
→ Optional MQTT / Kubios  

---

## Project Structure

```text
main.py         - Entry point and main loop
config.py       - System configuration and constants
hardware.py     - ADC, OLED, LED, encoder setup
sampling.py     - Timer, FIFO, and data acquisition
processing.py   - Signal processing, BPM and HRV
display.py      - OLED screens and UI
menu.py         - User navigation and control
storage.py      - JSON saving and history
network.py      - Wi-Fi, MQTT, Kubios

---

## Goals

The main goal of this project is to design and implement a fully functional embedded system for pulse and HRV monitoring.

Key objectives:

- Build a stable real-time sampling system at 250 Hz
- Implement reliable heartbeat detection
- Calculate realistic BPM values
- Perform local HRV analysis
- Store and display measurement history
- Extend the system with network capabilities

---

## Hardware

- Raspberry Pi Pico
- PPG sensor with analog output
- OLED display (SSD1306, I2C)
- Rotary encoder with push button
- LEDs

---

## Project Status

Work in progress.

Current stage:
- Project setup and architecture planning

Next steps:
- Implement sampling pipeline using ADC, timer, and FIFO

---

## Images

(coming soon)

---

## Authors

Hardware 2 student project  
Metropolia University of Applied Sciences