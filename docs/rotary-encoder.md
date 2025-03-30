Rotary Encoder
==============

A rotary encoder can be used in two different ways: By polling and by device overlay. Polling means checking the pins
over and over again in a short period of time, the device overlay on the other hand is an event based system. The device
overlay way is used here, because it is much more reliable.

## Wiring

A rotary encoder has two channels, channels A and B. On the KY-040 they are named CLK and DT for some reason, indicating
some clock and data pins, which is not really the case.

Connecting the rotary switch is optional. It can be used to call any function for debugging, like resetting the display.

| Rotary Encoder Pin | Raspberry Pi Pin |
|--------------------|------------------|
| GND                | GND              |
| +                  | VCC (3.3 V)      |
| CLK                | GPIO 22          |
| DT                 | GPIO 23          |
| SW                 | GPIO 27 / NC     |

## Configuration

To register the rotary encoder as a device, add this to `/boot/firmware/config.txt`:

```
dtoverlay=rotary-encoder,pin_a=22,pin_b=23,relative_axis=1,steps-per-period=1
```

Reboot the Pi.

Install ``evtest`` if not already done:
```bash
sudo apt install evtest
```

Calling ``evtest`` should return a list of input devices:
```
No device specified, trying to scan all of /dev/input/event*
Not running as root, no devices may be available.
Available devices:
/dev/input/event0:      rotary@16
/dev/input/event1:      vc4-hdmi
/dev/input/event2:      vc4-hdmi HDMI Jack
```

The rotary shows up as ``/dev/input/event0``. Quit the command with ``Ctrl+C``.
