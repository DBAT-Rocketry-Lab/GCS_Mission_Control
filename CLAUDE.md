# GCS Mission Control - Claude Code Guide

## Project Overview
This is a Ground Control Station (GCS) for model rocketry designed to support telemetry acquisition, vehicle monitoring, and future command & control during static testing and flight operations.

## Project Structure
- `launch_rockets_GUI.py` - Flight operations interface for relay/LED control
- `thrust_GUI.py` - Static fire telemetry console with live plotting and video recording
- `new_basic2.py` - Duplicate/similar to thrust_GUI.py (likely a development version)
- `README.md` - Detailed project documentation with status and features
- `requirements.txt` - Python dependencies

## Key Features
### Flight Operations (`launch_rockets_GUI.py`)
- ESP32-based relay and LED control
- Connection testing via ping
- Simple GUI control interface

### Static Fire Operations (`thrust_GUI.py` and `new_basic2.py`)
- Real-time telemetry plotting using matplotlib
- System monitoring and control (ARM, LAUNCH, END, RST, TARE)
- Video recording of telemetry data
- WiFi socket communication with ESP32 sensor devices
- Dark mode GUI using customtkinter

## Development Guidelines
1. **ESP32 Configuration**: Update IP addresses in the GUI files as needed for your network
2. **Dependencies**: Install requirements with `pip install -r requirements.txt`
3. **GUI Libraries**: 
   - customtkinter for modern Tkinter-based UI
   - matplotlib for real-time plotting
4. **Communication**: Uses TCP sockets to communicate with ESP32 devices on port 8080

## Common Tasks
- To run the flight operations GUI: `python launch_rockets_GUI.py`
- To run the static fire console: `python thrust_GUI.py` or `python new_basic2.py`
- To update dependencies: `pip install -r requirements.txt --upgrade`

## Telemetry Protocol
The ESP32 devices send numerical telemetry data over WiFi sockets, which is parsed and plotted in real-time. The system supports:
- Real-time plotting with zoom and pan
- Data recording to MP4 video
- System state monitoring (armed, launched, etc.)

## Notes
- Both thrust_GUI.py and new_basic2.py appear to have similar functionality - check which is the active development version
- IP addresses are hardcoded and will need to be updated for different networks
- The project uses dark mode themes consistently across all GUIs