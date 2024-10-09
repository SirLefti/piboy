NEO-6M GPS module
================

The NEO-6M is a GPS module communicating via UART. It provides the current position of the device.

## Wiring

The NEO-6M module has four pins in total.

| NEO-6M Pin | Raspberry Pi Pin |
|------------|------------------|
| GND        | GND              |
| VCC        | VCC (5 V)        |
| RX         | TX (GPIO 14)     |
| TX         | RX (GPIO 15)     |

The RX pin on the module can be skipped and is not needed for now.

## Configuration

Add the following entry to `/boot/firmware/config.txt`:
```
enable_uart=1
```

Remove this from `/boot/firmware/cmdline.txt`:
```
console=serial0,115200 
```

Reboot the Pi.

Check if the module is wired correctly and sends some data:
```bash
sudo cat /dev/serial0
```
It might return lines like this:
```
$GPTXT,01,01,01,NMEA unknown msg*58
```

If the blue LED on the module is blinking, it has already found its position and sends messages with the position. Go
outside or close to a window and wait a few minutes if it does not blink.

Open a python console and test it out:
```pycon
>>> import serial
>>> import io
>>> import pynmea2
>>> device = serial.Serial('/dev/serial0', baudrate=9600, timeout=0.5)
>>> io_wrapper = io.TextIOWrapper(io.BufferedRWPair(device, device))
>>> while True:
...     data = io_wrapper.readline()
...     if data[0:6] == '$GPRMC':
...         message = pynmea2.parse(data)
...         print('lat:', message.latitude, 'lon:', message.longitude)
```
