#!/usr/bin/env python3

import subprocess
import sys
import time
import shlex
from dataclasses import dataclass, field
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    from rich.theme import Theme
    from rich import box
except ImportError:
    print("Missing dependency: run  pip install rich")
    sys.exit(1)

# ──────────────────────── CONFIGURATION ──────────────────────────
USTREAMER_PATH = "./ustreamer/ustreamer"
RES            = "640x480"
FPS            = "15"
START_PORT     = 8000
MAVLINK_CMD    = "mavlink-routerd"

THEME = Theme({
    "banner":    "bold #00b4d8",
    "heading":   "bold #0077b6",
    "ok":        "bold #00b4d8",
    "warn":      "bold #f4a261",
    "error":     "bold #e63946",
    "dim":       "#4a5568",
    "cmd":       "bold #90e0ef",
    "info":      "#caf0f8",
    "muted":     "#4a5568",
})

console = Console(theme=THEME)

@dataclass
class StreamInfo:
    device:  str
    port:    int
    res:     str
    fps:     str
    process: Optional[subprocess.Popen] = field(default=None, repr=False)

    @property
    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    @property
    def status(self) -> str:
        if self.process is None:
            return "stopped"
        if self.process.poll() is None:
            return "running"
        return "error"

class MavlinkRouter:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None

    @property
    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    @property
    def status(self) -> str:
        if self.process is None:
            return "stopped"
        if self.process.poll() is None:
            return "running"
        return "error"

    def start(self):
        if self.running:
            console.print("[warn]MAVLink Router is already running.[/]")
            return
        try:
            self.process = subprocess.Popen(
                shlex.split(MAVLINK_CMD),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.4)
            if self.running:
                console.print("[ok]✓ MAVLink Router started.[/]")
            else:
                console.print("[error]✗ MAVLink Router failed to start.[/]")
        except FileNotFoundError:
            console.print(f"[error]✗ Command not found: {MAVLINK_CMD}[/]")

    def stop(self):
        if not self.running:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.process = None
        console.print("[ok]✓ MAVLink Router stopped.[/]")

# ──────────────────────── CONTROL FUNCTIONS ──────────────────────

def set_camera_ctrl(device: str, ctrl: str, value: int, silent=False):
    try:
        cmd = ["v4l2-ctl", "-d", device, "--set-ctrl", f"{ctrl}={value}"]
        subprocess.run(cmd, check=True, capture_output=True)
        if not silent:
            console.print(f"[ok]✓ {ctrl.capitalize()} set to {value} for {device}[/]")
    except subprocess.CalledProcessError:
        console.print(f"[error]✗ Failed to set {ctrl} for {device}.[/]")

def _is_intel_video(dev: str) -> bool:
    try:
        info = subprocess.check_output(
            ["udevadm", "info", "--query=all", "--name", dev],
            text=True, stderr=subprocess.DEVNULL
        )
        return "ID_VENDOR_ID=8086" in info
    except subprocess.CalledProcessError:
        return False

def discover_cameras() -> list[str]:
    result = subprocess.run(
        ["v4l2-ctl", "--list-devices"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0 and not result.stdout.strip():
        return []
    lines = result.stdout.splitlines()
    cameras = []
    current_videos: list[str] = []
    current_is_intel = False

    def flush():
        nonlocal current_videos, current_is_intel
        if current_videos:
            if current_is_intel:
                if len(current_videos) >= 5:
                    cameras.append(current_videos[4])
            else:
                cameras.append(current_videos[0])
        current_videos = []
        current_is_intel = False

    for line in lines:
        line = line.strip()
        if not line: continue
        if not line.startswith("/dev"): flush()
        elif line.startswith("/dev/video"):
            current_videos.append(line)
            if not current_is_intel and _is_intel_video(line):
                current_is_intel = True
    flush()
    return cameras

def build_streams(devices: list[str]) -> dict[int, StreamInfo]:
    streams = {}
    for i, dev in enumerate(devices):
        port = START_PORT + i
        streams[port] = StreamInfo(device=dev, port=port, res=RES, fps=FPS)
    return streams
def start_stream(streams: dict[int, StreamInfo], port: int, res: str = RES):
    s = streams.get(port)
    if s and not s.running:
        s.res = res
        cmd = [
            USTREAMER_PATH, f"--device={s.device}", "--host=0.0.0.0",
            f"--port={s.port}", "--format=mjpeg", f"--resolution={s.res}",
            f"--desired-fps={s.fps}", "--allow-origin=*"
        ]
        s.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        if s.running:
            console.print(f"[ok]✓ Stream started — {s.device} → port {s.port}[/]")
def stop_stream(streams: dict[int, StreamInfo], port: int):
    s = streams.get(port)
    if s and s.running:
        s.process.terminate()
        s.process = None
        console.print(f"[ok]✓ Stream {port} stopped.[/]")

# ──────────────────────── UI COMPONENTS ──────────────────────────

def status_table(streams: dict[int, StreamInfo], mavlink: MavlinkRouter):
    tbl = Table(box=box.SIMPLE_HEAD, show_header=True, title="[heading]System Status[/]")
    tbl.add_column("Port", style="cmd", justify="right")
    tbl.add_column("Device", style="info")
    tbl.add_column("Status")
    for port in sorted(streams):
        s = streams[port]
        stat = Text("● running", style="ok") if s.running else Text("○ stopped", style="muted")
        tbl.add_row(str(s.port), s.device, stat)
    mv_stat = Text("● running", style="ok") if mavlink.running else Text("○ stopped", style="muted")
    tbl.add_row("MAV", MAVLINK_CMD, mv_stat)
    console.print(tbl)

def print_help():
    tbl = Table(box=box.SIMPLE, show_header=False)
    cmds = [
        ("start all", "Start MAVLink and ALL cameras"),
        ("refresh all", "Re-scan hardware & reset ports"),
        ("set br <port> <val>", "Set Brightness for one camera"),
        ("set br all <val>", "Set Brightness for ALL cameras"),
        ("set ct <port> <val>", "Set Contrast for one camera"),
        ("set ct all <val>", "Set Contrast for ALL cameras"),
        ("set port bt <val>", "Set global starting port"),
        ("set port ct <old> <new>", "Remap a specific camera port"),
        ("list / help", "Status or Commands"),
        ("exit", "Shut down all and quit"),
    ]
    for c, d in cmds: tbl.add_row(c, d)
    console.print(Panel(tbl, title="[heading]Commands[/]", border_style="dim"))

# ──────────────────────── MAIN LOOP ──────────────────────────────

def main():
    global START_PORT
    console.clear()
    devices = discover_cameras()
    streams = build_streams(devices)
    mavlink = MavlinkRouter()
    status_table(streams, mavlink)

    try:
        while True:
            raw = console.input("[cmd]▶[/] ").strip().lower()
            if not raw: continue
            parts = raw.split()

            if raw == "help": print_help()
            elif raw == "list": status_table(streams, mavlink)
            elif raw in ["exit", "quit"]: break
            
            elif parts[0] == "start":
                if "all" in parts:
                    mavlink.start()
                    for p in streams: start_stream(streams, p)
                elif "mavlink" in parts: mavlink.start()
                elif "cam" in parts: start_stream(streams, int(parts[2]))

            elif parts[0] == "stop":
                if "all" in parts:
                    for p in streams: stop_stream(streams, p)
                elif "mavlink" in parts: mavlink.stop()
                elif "cam" in parts: stop_stream(streams, int(parts[2]))

            elif parts[0] == "refresh" and "all" in parts:
                for p in list(streams.keys()): stop_stream(streams, p)
                devices = discover_cameras()
                streams = build_streams(devices)
                console.print("[ok]✓ Discovery refreshed.[/]")
                status_table(streams, mavlink)

            elif parts[0] == "set":
                try:
                    # BRIGHTNESS logic
                    if parts[1] == "br":
                        if parts[2] == "all":
                            val = int(parts[3])
                            for p in streams: set_camera_ctrl(streams[p].device, "brightness", val, silent=True)
                            console.print(f"[ok]✓ Brightness set to {val} for ALL cameras.[/]")
                        else:
                            set_camera_ctrl(streams[int(parts[2])].device, "brightness", int(parts[3]))
                    
                    # CONTRAST logic
                    elif parts[1] == "ct":
                        if parts[2] == "all":
                            val = int(parts[3])
                            for p in streams: set_camera_ctrl(streams[p].device, "contrast", val, silent=True)
                            console.print(f"[ok]✓ Contrast set to {val} for ALL cameras.[/]")
                        else:
                            set_camera_ctrl(streams[int(parts[2])].device, "contrast", int(parts[3]))

                    elif parts[1] == "port" and parts[2] == "bt":
                        START_PORT = int(parts[3])
                        console.print(f"[ok]✓ Base port set to {START_PORT}. Run 'refresh all' to apply.")
                    
                    elif parts[1] == "port" and parts[2] == "ct":
                        old_p, new_p = int(parts[3]), int(parts[4])
                        if old_p in streams:
                            streams[new_p] = streams.pop(old_p)
                            streams[new_p].port = new_p
                            console.print(f"[ok]✓ Port {old_p} moved to {new_p}")
                except (IndexError, ValueError, KeyError):
                    console.print("[error]Invalid syntax. Example: 'set br 8000 120' or 'set br all 120'[/]")

            console.print()

    except Exception as e:
        console.print(f"[error]Error: {e}[/]")
    finally:
        console.print("\n[warn]⚡ Shutting down...[/]")
        for p in streams: stop_stream(streams, p)
        if mavlink.running: mavlink.stop()

if __name__ == "__main__":
    main()
