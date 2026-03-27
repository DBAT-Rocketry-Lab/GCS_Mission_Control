
import customtkinter as ctk
import requests
import subprocess
import platform
import threading
import time

ESP_IP = "172.24.80.44"  # Update with your ESP IP

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.geometry("350x400")
app.title("Relay & LED Control")

def ping_esp():
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(["ping", param, "1", "-w", "2", ESP_IP], 
                           capture_output=True, text=True)
    return result.returncode == 0

def safe_request(endpoint):
    if not ping_esp():
        status.configure(text="NO CONNECTION")
        return False
    try:
        response = requests.get(f"http://{ESP_IP}/{endpoint}", timeout=2)
        status.configure(text=f"{endpoint} OK")
        return True
    except:
        status.configure(text="CONNECTION ERROR")
        return False

# RELAY BUTTONS
relay_on_btn = ctk.CTkButton(app, text="RELAY ON", 
                           command=lambda: safe_request("RELAY_ON"))
relay_off_btn = ctk.CTkButton(app, text="RELAY OFF", 
                            command=lambda: safe_request("RELAY_OFF"))

# LED BUTTONS
led_on_btn = ctk.CTkButton(app, text="LED ON", 
                         command=lambda: safe_request("LED_ON"))
led_off_btn = ctk.CTkButton(app, text="LED OFF", 
                          command=lambda: safe_request("LED_OFF"))

# TEST BUTTON
test_btn = ctk.CTkButton(app, text="TEST CONNECTION", 
                        command=lambda: ping_esp() and 
                        status.configure(text="PING OK") or 
                        status.configure(text="PING FAIL"))

# LAYOUT
ctk.CTkLabel(app, text="ESP32 Relay/LED Control", font=("Arial", 20)).pack(pady=10)
status = ctk.CTkLabel(app, text="STATUS: READY")
status.pack(pady=5)

test_btn.pack(pady=10)

ctk.CTkLabel(app, text="RELAY", font=("Arial", 16)).pack(pady=(20,5))
relay_on_btn.pack(pady=5)
relay_off_btn.pack(pady=5)

ctk.CTkLabel(app, text="LED", font=("Arial", 16)).pack(pady=(20,5))
led_on_btn.pack(pady=5)
led_off_btn.pack(pady=5)

app.mainloop()
