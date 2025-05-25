# Bongo LED Control System (Restructured)

This project provides a robust and modular framework for controlling a matrix of LEDs on a Raspberry Pi. It decouples pattern logic from individual LED control, allowing for concurrent and independent operations on each LED.

## Features

* **Individual LED Control:** Each LED is managed by its own thread, allowing for independent brightness ramps, holds, and fades.
* **Hardware Abstraction:** Supports various LED hardware configurations (Mock, PCA9685, Raspberry Pi PWM) through a common `AbstractLED` interface.
* **Command-Based Operations:** LEDs respond to defined `LEDOperation` commands, specifying start time, target brightness, ramp, hold, and fade durations.
* **Pattern Generators:** Higher-level functions generate sequences of `LEDOperation` commands for complex visual effects.
* **Testable Architecture:** Includes unit tests for hardware abstractions and core LED control logic.

## Project Structure