import cv2
import numpy as np

# ===================== CONFIG =====================
cam_index = 1

deadzone = 0.02        # stop condition threshold
arrow_scale = 200      # visual only
min_matches = 10
# ==================================================

# -------- Camera --------
cap = cv2.VideoCapture(cam_index)

# -------- ORB detector --------
orb = cv2.ORB_create(
    nfeatures=1000,
    scaleFactor=1.2,
    nlevels=8
)

# -------- State --------
ref_kp = None
ref_des = None

print("Controls:")
print("  R  → set reference frame")
print("  Q  → quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = frame.shape[:2]

    # Detect features in current frame
    kp, des = orb.detectAndCompute(gray, None)

    dx_norm = 0.0
    dy_norm = 0.0
    at_setpoint = False

    if ref_des is not None and des is not None:
        # -------- Feature matching --------
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(ref_des, des)

        if len(matches) >= min_matches:
            shifts_x = []
            shifts_y = []

            for m in matches:
                x_ref, y_ref = ref_kp[m.queryIdx].pt
                x_cur, y_cur = kp[m.trainIdx].pt

                shifts_x.append(x_cur - x_ref)
                shifts_y.append(y_cur - y_ref)

            dx_px = np.mean(shifts_x)
            dy_px = np.mean(shifts_y)

            # -------- Normalize to [-1, 1] --------
            dx_norm = dx_px / (w / 2)
            dy_norm = dy_px / (h / 2)

            dx_norm = max(-1.0, min(1.0, dx_norm))
            dy_norm = max(-1.0, min(1.0, dy_norm))

            # -------- Stop condition --------
            at_setpoint = (
                abs(dx_norm) < deadzone and
                abs(dy_norm) < deadzone
            )

            # -------- Visualization --------
            center = (w // 2, h // 2)
            arrow_end = (
                int(center[0] + dx_norm * arrow_scale),
                int(center[1] + dy_norm * arrow_scale)
            )

            arrow_color = (0, 255, 0) if at_setpoint else (0, 0, 255)

            cv2.arrowedLine(
                frame,
                center,
                arrow_end,
                arrow_color,
                3
            )

            cv2.putText(
                frame,
                f"dx: {dx_norm:.2f}  dy: {dy_norm:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                arrow_color,
                2
            )

            status_text = "HOLD" if at_setpoint else "CORRECT"
            cv2.putText(
                frame,
                status_text,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                arrow_color,
                2
            )

        else:
            cv2.putText(
                frame,
                "Not enough matches",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

    cv2.imshow("Visual Set-Point (Normalized)", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        ref_kp, ref_des = orb.detectAndCompute(gray, None)
        print("Reference frame set")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

