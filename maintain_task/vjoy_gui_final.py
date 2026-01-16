import pyvjoy
import tkinter as tk

# --- vJoy setup ---
j = pyvjoy.VJoyDevice(1)

MAX = 32768         # New max value
CENTER = MAX // 2   # 16384

# --- Helper functions ---
def clamp(v):
    return max(0, min(MAX, v))

def slider_to_vjoy(value):
    """
    Map slider value [0.0, 1.0] to [0, MAX]
    So 0.5 maps to CENTER (16384)
    """
    return int(value * MAX)

# --- GUI callbacks ---
def update_values_display():
    display_text = (
        f"Roll (X): {roll_val} (0x{roll_val:04X})\n"
        f"Pitch (Y): {pitch_val} (0x{pitch_val:04X})\n"
        f"Yaw (RZ): {yaw_val} (0x{yaw_val:04X})\n"
        f"Throttle (Z): {throttle_val} (0x{throttle_val:04X})"
    )
    values_label.config(text=display_text)
    print(display_text)
    print("-" * 40)

def on_roll(val):
    global roll_val
    roll_val = clamp(slider_to_vjoy(float(val)))
    j.set_axis(pyvjoy.HID_USAGE_X, roll_val)
    update_values_display()

def on_pitch(val):
    global pitch_val
    pitch_val = clamp(slider_to_vjoy(float(val)))
    j.set_axis(pyvjoy.HID_USAGE_Y, pitch_val)
    update_values_display()

def on_yaw(val):
    global yaw_val
    yaw_val = clamp(slider_to_vjoy(float(val)))
    j.set_axis(pyvjoy.HID_USAGE_RZ, yaw_val)
    update_values_display()

def on_throttle(val):
    global throttle_val
    throttle_val = clamp(slider_to_vjoy(float(val)))
    j.set_axis(pyvjoy.HID_USAGE_Z, throttle_val)
    update_values_display()

def center_all_axes():
    roll_slider.set(0.5)
    pitch_slider.set(0.5)
    yaw_slider.set(0.5)
    throttle_slider.set(0.5)

# --- Initialize globals ---
roll_val = CENTER
pitch_val = CENTER
yaw_val = CENTER
throttle_val = CENTER

# --- GUI ---
root = tk.Tk()
root.title("Virtual Joystick Control - Range 0 to 32768 with Center 16384")

tk.Label(root, text="Roll (X)").pack()
roll_slider = tk.Scale(root, from_=0, to=1, resolution=0.001,
                       orient="horizontal", command=on_roll)
roll_slider.pack(fill="x")

tk.Label(root, text="Pitch (Y)").pack()
pitch_slider = tk.Scale(root, from_=0, to=1, resolution=0.001,
                        orient="horizontal", command=on_pitch)
pitch_slider.pack(fill="x")

tk.Label(root, text="Yaw (RZ)").pack()
yaw_slider = tk.Scale(root, from_=0, to=1, resolution=0.001,
                      orient="horizontal", command=on_yaw)
yaw_slider.pack(fill="x")

tk.Label(root, text="Throttle (Z)").pack()
throttle_slider = tk.Scale(root, from_=0, to=1, resolution=0.001,
                           orient="horizontal", command=on_throttle)
throttle_slider.pack(fill="x")

center_button = tk.Button(root, text="Center All Axes", command=center_all_axes)
center_button.pack(pady=10)

values_label = tk.Label(root, text="", font=("Courier", 12), justify="left")
values_label.pack()

# Set sliders to center on start
center_all_axes()

root.mainloop()
