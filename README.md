![High Five In Action](pic.png?raw=true "High Five In Action")

A raspberry pi powered bot that lets people high five me remotely.

The `hw/hw.py` file will tell you how to wire up the components.

Originally the code was completely in Golang, but I had trouble getting PWM to
work reliably, both in hardware and software, so I rewrote the hardware interacting
code in Python.
