PiBoy
=========================

Build your own Pip-Boy with some useful features for real-life using your Raspberry Pi.

## Hardware

 - Raspberry Pi (any full size board should work)
 - 3.5" SPI display module (with an ILI9486 display driver chip)

## Installation

Install system dependencies:
````bash
sudo apt install build-essential git usbmount python3 python3-dev python3-smbus python3-venv fonts-freefont-ttf libjpeg-dev libatlas-base-dev libopenjp2-7-dev
````

Make sure the following entry in ``/lib/systemd/system/systemd-udevd.service`` matches and reboot after changes:
````bash
PrivateMount=no
````

Clone repository and go into it:
````bash
git clone https://github.com/SirLefti/piboy
cd piboy
````

Create a virtual environment:
````bash
python -m venv .venv
````

Install python dependencies:
````bash
.venv/bin/pip install -r requirements.txt
````

Edit the crontab with ``crontab -e`` and add the following:
````bash
@reboot cd /home/pi/piboy && .venv/bin/python piboy.py &
````
