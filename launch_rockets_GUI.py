
import socket
import threading
import time

import customtkinter as ctk

# ================== CONFIG ==================
ESP_IP = "10.34.142.190"
ESP_PORT = 8080

COUNTDOWN_S = 5
CHECK_INTERVAL_S = 2
SOCKET_TIMEOUT_S = 2

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ControlGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Static Fire Control Console")
        self.geometry("420x600")

        self.running = True
        self.connected = False
        self.armed = False
        self.led_on = False
        self.countdown = 0
        self.countdown_active = False

        self.request_lock = threading.Lock()

        self._build_ui()

        threading.Thread(
            target=self._connection_monitor,
            daemon=True,
        ).start()

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ================== UI ==================

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="CONTROL",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(20, 5))

        status_row = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        status_row.pack(pady=5)

        self.conn_dot = ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=28),
            text_color="gray",
        )
        self.conn_dot.pack(side="left", padx=8)

        self.status = ctk.CTkLabel(
            status_row, text="Connecting..."
        )
        self.status.pack(side="left")

        self.led_btn = ctk.CTkButton(
            self,
            text="LED ON",
            command=self.toggle_led,
        )
        self.led_btn.pack(
            fill="x", padx=40, pady=(20, 8)
        )

        self.arm_btn = ctk.CTkButton(
            self,
            text="ARM",
            fg_color="#ff8c00",
            hover_color="#cc7000",
            command=self.arm,
        )
        self.arm_btn.pack(fill="x", padx=40, pady=8)

        self.launch_btn = ctk.CTkButton(
            self,
            text="LAUNCH",
            fg_color="#b22222",
            hover_color="#8b0000",
            command=self.launch,
        )
        self.launch_btn.pack(fill="x", padx=40, pady=8)

        self.countdown_label = ctk.CTkLabel(
            self,
            text="READY",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.countdown_label.pack(pady=5)

        self.status_btn = ctk.CTkButton(
            self,
            text="GET STATUS",
            command=self.get_status,
        )
        self.status_btn.pack(
            fill="x", padx=40, pady=5
        )

        self.log_box = ctk.CTkTextbox(
            self, height=200
        )
        self.log_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(15, 20),
        )

        self.log("System initialized.")
        self.log(f"TCP target: {ESP_IP}:{ESP_PORT}")

    # ================== TCP NETWORK ==================

    def _request(self, command):
        """Send one newline-terminated TCP command and read its reply."""
        with self.request_lock:
            try:
                with socket.create_connection(
                    (ESP_IP, ESP_PORT),
                    timeout=SOCKET_TIMEOUT_S,
                ) as sock:

                    sock.settimeout(SOCKET_TIMEOUT_S)
                    sock.sendall(
                        (command + "\n").encode("utf-8")
                    )

                    response = bytearray()

                    while len(response) < 1024:
                        chunk = sock.recv(1)

                        if not chunk:
                            break

                        if chunk == b"\n":
                            break

                        if chunk != b"\r":
                            response.extend(chunk)

                    if not response:
                        return False, "Empty response"

                    return True, response.decode(
                        "utf-8", errors="replace"
                    )

            except (OSError, TimeoutError) as exc:
                return False, str(exc)

    def send_cmd(self, command, callback=None):
        """Run network calls off the GUI thread."""

        def worker():
            ok, response = self._request(command)

            if self.running:
                self.after(
                    0,
                    self._handle_response,
                    command,
                    ok,
                    response,
                    callback,
                )

        threading.Thread(
            target=worker, daemon=True
        ).start()

    def _handle_response(
        self, command, ok, response, callback
    ):
        if not self.running:
            return

        if ok:
            self.log(f"> {command}")
            self.log(f"< {response}")

            self._show_connection(True)

            if command == "arm" and response == "ARMED":
                self.armed = True

            elif command == "disarm" and response == "DISARMED":
                self.armed = False

            elif command == "led_on" and response == "LED ON":
                self.led_on = True
                self.led_btn.configure(text="LED OFF")

            elif command == "led_off" and response == "LED OFF":
                self.led_on = False
                self.led_btn.configure(text="LED ON")

        else:
            self.log(f"{command} FAILED: {response}")
            self._show_connection(False)

        if callback:
            callback(ok, response)

    # ================== CONNECTION MONITOR ==================

    def _connection_monitor(self):
        while self.running:
            ok, _ = self._request("ping")

            if not self.running:
                break

            self.after(0, self._show_connection, ok)
            time.sleep(CHECK_INTERVAL_S)

    def _show_connection(self, ok):
        if not self.running:
            return

        if self.connected != ok:
            self.connected = ok
            self.log(
                "ESP32 connected."
                if ok else "ESP32 connection lost."
            )

        self.conn_dot.configure(
            text_color="green" if ok else "red"
        )
        self.status.configure(
            text=(
                f"ESP32 connected ({ESP_IP})"
                if ok else "NO CONNECTION"
            )
        )

    # ================== BUTTONS ==================

    def toggle_led(self):
        self.send_cmd(
            "led_off" if self.led_on else "led_on"
        )

    def arm(self):
        self.send_cmd("arm")

    def get_status(self):
        self.send_cmd("status")

    # ================== COUNTDOWN DISPLAY ==================

    def launch(self):
        if not self.armed:
            self.log("Not armed. Press ARM first.")
            return

        if self.countdown_active:
            self.log("Countdown already running.")
            return

        self.countdown_active = True
        self.countdown = COUNTDOWN_S

        self.launch_btn.configure(state="disabled")
        self.log("--- COUNTDOWN DISPLAY STARTED ---")

        self._countdown_step()

    def _countdown_step(self):
        if not self.running:
            return

        if self.countdown > 0:
            self.countdown_label.configure(
                text=f"T-{self.countdown}"
            )
            self.log(f"T-{self.countdown}")

            self.countdown -= 1
            self.after(1000, self._countdown_step)

        else:
            self.countdown_label.configure(
                text="COUNTDOWN COMPLETE"
            )
            self.log(
                "Countdown display complete. "
                "No relay command was sent."
            )

            self.countdown_active = False
            self.launch_btn.configure(state="normal")

    # ================== UTIL ==================

    def log(self, message):
        if not self.running:
            return

        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert(
            "end", f"[{timestamp}] {message}\n"
        )
        self.log_box.see("end")

    def destroy(self):
        self.running = False
        super().destroy()


if __name__ == "__main__":
    app = ControlGUI()
    app.mainloop()
