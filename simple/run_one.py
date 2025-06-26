#!/usr/bin/env python3
import board
import busio
from adafruit_pca9685 import PCA9685

# Constants
PCA9685_ADDRESS = 0x40
LED_CHANNEL = 4     # Channels are 0-15


def main():
    # Initialize I2C and PCA9685
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c, address=PCA9685_ADDRESS)
    pca.frequency = 60
    for i in range(16):
        pca.channels[i].duty_cycle = 0

    # Turn on LED (full brightness)
    # pca.channels[LED_CHANNEL].duty_cycle = 0xFFFF

    print(f"LED on channel {LED_CHANNEL} turned on")
    # Add this to your working run_one.py
    pca.channels[3].duty_cycle = 65535
    print(f"Channel: {pca.channels[3]} duty_cycle: 65535")
    print(f"Duty: {pca.channels[3].duty_cycle}")


if __name__ == "__main__":
    main()