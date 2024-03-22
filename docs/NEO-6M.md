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

Add the following entry to `/boot/config.txt`:
```
enable_uart=1
```

Remove this from `/boot/cmdline.txt`:
```
console=serial0,115200 
```

Reboot the Pi.

Check if the module is wired correctly and sends some data:
```bash
sudo cat /dev/ttyAMA0
```
It might return lines like this:
```
$GPTXT,01,01,01,NMEA unknown msg*58
```

If the blue LED on the module is blinking, it has already found its position and sends messages with the position. Go
outside or close to a window and wait a few minutes if it does not blink.

