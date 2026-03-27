import threading
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FFMpegWriter
import serial
import customtkinter as ctk
import time

# ================== CONFIG ==================
SERIAL_PORT = "/dev/ttyUSB0"   # 🔁 CHANGE THIS
BAUDRATE = 115200

MAX_POINTS = 1000
PLOT_REFRESH_MS = 30
ZOOM_FACTOR = 1.05
BUFFER_RATIO = 0.2

# ================== APP ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ThrustGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Static Fire Telemetry Console")
        self.geometry("1200x700")

        # ---------- STATE ----------
        self.ser = None
        self.running = True
        self.start_time = time.time()
        self.zoom_scale = 1.0

        self.times = deque(maxlen=MAX_POINTS)
        self.values = deque(maxlen=MAX_POINTS)

        self.countdown = None
        self.led_on = False
        self.recording = False
        self.video_frames = []

        # ---------- LAYOUT ----------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_controls()
        self._build_plot()
        self._build_log_and_led()

        # ---------- SERIAL ----------
        self.init_serial()
        self.start_serial_thread()

        # ---------- PLOT LOOP ----------
        self.after(PLOT_REFRESH_MS, self.update_plot)

    # ================== UI ==================

    def _build_controls(self):
        self.ctrl = ctk.CTkFrame(self, width=200)
        self.ctrl.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(
            self.ctrl, text="CONTROL",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        ctk.CTkButton(self.ctrl, text="RST", command=self.reset)\
            .pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.ctrl, text="TARE", command=self.tare)\
            .pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self.ctrl,
            text="ARM",
            fg_color="#ff8c00",
            hover_color="#cc7000",
            command=self.arm
        ).pack(fill="x", padx=20, pady=10)

        self.launch_btn = ctk.CTkButton(
            self.ctrl,
            text="LAUNCH",
            fg_color="#b22222",
            hover_color="#8b0000",
            command=self.launch
        )
        self.launch_btn.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(self.ctrl, text="END", command=self.end_record)\
            .pack(fill="x", padx=20, pady=5)

    def _build_plot(self):
        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Live Telemetry")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("ADC Value")
        self.ax.grid(True)

        self.line, = self.ax.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig, self.main)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _build_log_and_led(self):
        bottom = ctk.CTkFrame(self.main)
        bottom.grid(row=1, column=0, sticky="ew", pady=10)
        bottom.grid_columnconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(bottom, height=120)
        self.log_box.grid(row=0, column=0, sticky="ew", padx=10)
        self.log("System initialized.")

        self.led = ctk.CTkLabel(
            bottom, text="●",
            font=ctk.CTkFont(size=36),
            text_color="gray"
        )
        self.led.grid(row=0, column=1, padx=20)

    # ================== SERIAL ==================

    def init_serial(self):
        try:
            self.ser = serial.Serial(
                SERIAL_PORT,
                BAUDRATE,
                timeout=0.01
            )
            self.log("ESP32 connected over USB serial.")
        except Exception as e:
            self.ser = None
            self.log(f"Serial connection failed: {e}")

    def start_serial_thread(self):
        threading.Thread(target=self.serial_reader, daemon=True).start()

    def serial_reader(self):
        while self.running:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode().strip()
                    val = float(line)

                    t = time.time() - self.start_time
                    self.times.append(t)
                    self.values.append(val)

                    if self.recording:
                        self.video_frames.append(
                            (list(self.times), list(self.values))
                        )
                except:
                    pass
            time.sleep(0.001)

    # ================== PLOT ==================

    def update_plot(self):
        if self.times:
            self.line.set_data(self.times, self.values)
            self.ax.set_xlim(self.times[0], self.times[-1])

            ymin, ymax = min(self.values), max(self.values)
            self.zoom_scale *= ZOOM_FACTOR ** (-1 / len(self.values))
            margin = (ymax - ymin) * BUFFER_RATIO * self.zoom_scale or 1
            self.ax.set_ylim(ymin - margin, ymax + margin)

            self.canvas.draw_idle()

        self.after(PLOT_REFRESH_MS, self.update_plot)

    # ================== BUTTONS ==================

    def reset(self):
        self.times.clear()
        self.values.clear()
        self.start_time = time.time()
        self.zoom_scale = 1.0
        self.log("Plot reset.")

    def tare(self):
        self.send_cmd("t")
        self.log("Tare sent.")

    def arm(self):
        self.send_cmd("arm")
        self.log("System ARMED 🔐")

    def launch(self):
        self.recording = True
        self.video_frames.clear()
        self.countdown = 5
        self.log("--- RECORDING STARTED ---")
        self.launch_btn.configure(state="disabled")
        self.log("--- LAUNCH SEQUENCE INITIATED ---")
        self.led.configure(text_color="red")
        self._countdown_step()

    def _countdown_step(self):
        if self.countdown > 0:
            self.log(f"T-{self.countdown}")
            self.led_on = not self.led_on
            self.led.configure(
                text_color="red" if self.led_on else "gray"
            )
            self.countdown -= 1
            self.after(1000, self._countdown_step)
        else:
            self.led.configure(text_color="green")
            self.log("IGNITION 🔥")
            self.send_cmd("1")
            self.launch_btn.configure(state="normal")

    def end_record(self):
        if self.recording:
            self.recording = False
            self.log("Recording stopped. Saving MP4...")
            self.save_video()
        else:
            self.log("Not recording.")

    # ================== UTIL ==================

    def send_cmd(self, cmd):
        if self.ser:
            try:
                self.ser.write((cmd + "\n").encode())
            except:
                self.log("Serial TX failed.")

    def log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def destroy(self):
        self.running = False
        if self.ser:
            self.ser.close()
        super().destroy()


# ================== RUN ==================
if __name__ == "__main__":
    app = ThrustGUI()
    app.mainloop()
