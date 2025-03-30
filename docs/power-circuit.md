Power Circuit
=============

The power circuit provides battery power to this project, to use it without external power supply. It supports a 
standard 18650 battery cell, but can fit any other smaller sizes as well. 

## Parts
* 1x MT3608 power converter
* 1x TP4056 battery charging controller
* 1x 18650 Li-ion battery cell (others can fit as well)
* 1x toggle switch
* wires and soldering stuff

## Assembly

Solder the parts together as shown in the table and image below.

**IMPORTANT:** Set up the power converter to output 5.0 V before soldering the Pi to it. The Pi has no fuses to protect
itself from over-voltage via the pins. Charge the battery before configuring it.

**NOTE**: The switch is placed between the battery/charging controller and the power converter, because the power
converter would drain the battery over time if it was permanently connected to it.

| from          | to              |
|---------------|-----------------|
| battery+      | TP4056 B+       |
| battery-      | TP4056 B-       |
| TP4056 Out+   | Switch Center 1 |
| TP4056 Out-   | Switch Center 2 |
| Switch Left 1 | MT3608 VIn+     |
| Switch Left 2 | MT3608 VIn-     |
| MT3608 VOut+  | Pi Pin 2 (5V)   |
| MT3608 VOut-  | Pi Pin 6 (GND)  |

The complete circuit should look like this. Try to power it on like that to see if everything works. Also attach the
display module, because it has a relatively high power draw compared to the other components.
![power-circuit](power-circuit.jpg)
*Note: This example uses two separate cells instead of the single 18650 one. If using two separate cells, make sure they
are of the same type and have the same rated capacity. These are harvested from disposable e-vapes.*
