# Hardware 2 Pulse & HRV Monitor

## Overview

This project is a standalone pulse monitoring system built with Raspberry Pi Pico.

The system reads a PPG signal using ADC, samples it at 250 Hz, detects heartbeats, and calculates BPM. Everything runs directly on the Pico without needing a computer.

An OLED display shows the data, and a rotary encoder is used for control.

---

## Features

- Standalone operation
- PPG signal via ADC
- 250 Hz sampling (timer + FIFO)
- Heartbeat detection
- BPM calculation
- LED indication
- OLED display
- Rotary encoder control
- Basic HRV support
- Optional storage and network features

---

## System Flow

PPG Sensor
-> ADC
-> Timer Sampling
-> FIFO Buffer
-> Processing
-> Beat Detection
-> BPM Calculation
-> OLED Display

---

## Project Structure

main.py         - main program
config.py       - settings
hardware.py     - ADC, OLED, LED, encoder setup
sampling.py     - timer and FIFO
processing.py   - signal processing
display.py      - OLED output
menu.py         - user control
storage.py      - data saving
network.py      - optional features

---

## Goals

Build a simple embedded pulse monitor.

The system should:
- sample signal at 250 Hz
- detect heartbeats
- calculate BPM
- show data on OLED
- allow control with encoder

---

## Hardware

- Raspberry Pi Pico
- PPG sensor
- OLED (SSD1306)
- Rotary encoder
- LED

---

## Status

Work in progress.

Next step:
- implement sampling (ADC + timer + FIFO)

---

## Authors

Hardware 2 student project
Metropolia UAS
