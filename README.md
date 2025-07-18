# Smart Street Light System

This project is an IoT-powered **Smart Street Lighting System** designed to conserve energy and improve maintenance in rural or urban environments.

**Features**
- Real-time monitoring of street light status via a sleek `index.html` web dashboard.
- Integrated **infrared sensors** to detect human presence.
- **Temperature and photoresistor sensors** to adapt brightness dynamically based on climate and ambient light.
- **Manual override** buttons on the dashboard for quick control.
- Modular Python scripts to handle each sensor and system component.

**Tech Stack**
- **Raspberry Pi Pico** for hardware control
- **MicroPython** scripts for sensor integration
- **HTML/CSS/JS** for the dashboard interface

**Included Files**
- `index.html`: Web dashboard UI
- `IR_LED_AP.py`, `ir_receiver.py`, `light.py`, `manual_override.py`, `SmartStreetLight.py`, `temp_test.py`, `temperature.py`: Pico/MicroPython scripts for sensor and light control
- `B10G06.pdf`: Original design proposal

**Getting Started**
1. Clone this repo.
2. Set up your Raspberry Pi Pico with MicroPython.
3. Deploy the Python scripts and open index.html in a browser to monitor and control the lights.
