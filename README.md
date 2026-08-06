# GCS Mission Control

A modular Ground Control Station (GCS) for model rocketry, designed to support telemetry acquisition, vehicle monitoring, and future command & control during static testing and flight operations.

> [!NOTE]
> **Project Status:** Active Development

---

## Project Status

| Component | Description | Status |
|-----------|-------------|:------:|
| Repository Structure | Initial project organization and documentation | 🟢 Complete |
| System Architecture | High-level software architecture and module design | 🟢 Complete |
| Telemetry Protocol | Packet structure and communication protocol | 🟡 In Progress |
| Ground Station Backend | Telemetry reception, parsing, and logging | 🟡 In Progress |
| LoRa Communication | SX1278 integration and wireless telemetry | 🟡 In Progress |
| Flight Operations Interface | Launch monitoring and mission control | ⚪️ Planned |
| Static Fire Interface | Static test monitoring and data acquisition | 🟡 in Progress |
| Flight Computer Integration | Interface with onboard avionics | ⚪️ Planned |
| Documentation | Architecture, setup guides and API docs | ⚪️ Planned |

---
## Overview

Ground Control Station (GCS) Mission Control is an ongoing project focused on developing a centralized software platform for monitoring and managing model rocket operations.

The project currently consists of two independent development tracks:

### Flight Operations

A telemetry-focused ground station designed for launch operations.

Current development includes:

- Real-time telemetry acquisition
- Wireless communication interface
- Live onboard video integration
- Mission status visualization
- Future support for flight computer integration

---

### Static Fire Operations

A dedicated interface for propulsion testing.

Current objectives include:

- Monitoring static motor tests
- Sensor data visualization
- Test logging
- Future automated data analysis

---

The long-term objective is to unify both interfaces into a single modular application capable of supporting the complete development lifecycle of a model rocket—from propulsion testing to flight operations.

---

## Motivation

Ground Control Stations are a fundamental component of modern unmanned systems.

For multirotor platforms, mature open-source ecosystems such as **Mission Planner** and **QGroundControl** provide comprehensive interfaces for mission planning, telemetry, and vehicle monitoring.

In contrast, amateur rocketry lacks a widely adopted, modular, open-source ground station specifically designed for experimental launch vehicles.

Most university teams and hobbyist groups develop custom software tailored to their own hardware, resulting in duplicated effort and limited reusability.

This project aims to address that gap by developing a modular and extensible Ground Control Station that can serve as a reusable foundation for model rocket telemetry, propulsion testing, and future avionics development.

---
## Design Philosophy

The project follows a modular architecture where each subsystem can be developed and tested independently.

The Ground Control Station is intended to remain hardware-agnostic wherever possible, allowing different telemetry links, sensors, and flight computers to be integrated with minimal software changes.

Core design principles include:

- Modular software architecture
- Low-latency telemetry processing
- Extensible communication interfaces
- Separation of hardware and software layers
- Reusable components across multiple rocket missions
