import cv2
import numpy as np

cap = cv2.VideoCapture(0)

green_lower = green_upper = None
blue_lower = blue_upper = None


# ---------- COLOR CALIBRATION ----------
def calibrate_color(frame, roi):
    x, y, w, h = roi
    roi = frame[y:y+h, x:x+w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    lower = np.array([
        max(0, np.min(h) - 5),
        max(60, np.min(s) - 30),
        max(60, np.min(v) - 30)
    ], dtype=np.uint8)

    upper = np.array([
        min(179, np.max(h) + 5),
        255,
        255
    ], dtype=np.uint8)

    return lower, upper


# ---------- SHAPE DETECTION ----------
def detect_shape(cnt):
    area = cv2.contourArea(cnt)
    if area < 800:
        return None

    peri = cv2.arcLength(cnt, True)
    if peri == 0:
        return None

    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    v = len(approx)

    if v == 3:
        return "triangle"

    if v == 4:
        return "square"

    if v >= 8:
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            return None

        solidity = area / hull_area
        if solidity > 0.85:
            return "circle"
        else:
            return "cross"

    return None


# ---------- COUNT + DRAW ----------
def count_and_detect(mask, display, color):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    counts = {
        "triangle": 0,
        "square": 0,
        "circle": 0,
        "cross": 0
    }

    for cnt in contours:
        shape = detect_shape(cnt)
        if shape:
            counts[shape] += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)
            cv2.putText(display, shape, (x, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return counts


print("g = green | b = blue | q = quit")


# ---------- MAIN LOOP ----------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    display = frame.copy()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('g'):
        roi = cv2.selectROI("GREEN ROI", frame, False, False)
        green_lower, green_upper = calibrate_color(frame, roi)
        cv2.destroyWindow("GREEN ROI")

    if key == ord('b'):
        roi = cv2.selectROI("BLUE ROI", frame, False, False)
        blue_lower, blue_upper = calibrate_color(frame, roi)
        cv2.destroyWindow("BLUE ROI")

    y = 30

    # GREEN
    if green_lower is not None:
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        g = count_and_detect(green_mask, display, (0, 255, 0))
        for k, v in g.items():
            cv2.putText(display, f"Green {k}: {v}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            y += 30
        y += 10

    # BLUE
    if blue_lower is not None:
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        b = count_and_detect(blue_mask, display, (255, 0, 0))
        for k, v in b.items():
            cv2.putText(display, f"Blue {k}: {v}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            y += 30

    cv2.imshow("Stable Color + Shape Detection", display)

    if key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
