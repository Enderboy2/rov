import cv2
import numpy as np

cap = cv2.VideoCapture(0)

green_lower = green_upper = None
blue_lower = blue_upper = None

def calibrate_color(frame, roi):
    x, y, w, h = roi
    roi = frame[y:y+h, x:x+w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    lower = np.array([
        max(0, np.min(h) - 5),
        max(50, np.min(s) - 30),
        max(50, np.min(v) - 30)
    ], dtype=np.uint8)

    upper = np.array([
        min(179, np.max(h) + 5),
        255,
        255
    ], dtype=np.uint8)

    return lower, upper


print("g = green | b = blue | q = quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('g'):
        roi = cv2.selectROI("GREEN ROI", frame, False, False)
        green_lower, green_upper = calibrate_color(frame, roi)
        print("GREEN HSV:", green_lower, green_upper)
        cv2.destroyWindow("GREEN ROI")

    if key == ord('b'):
        roi = cv2.selectROI("BLUE ROI", frame, False, False)
        blue_lower, blue_upper = calibrate_color(frame, roi)
        print("BLUE HSV:", blue_lower, blue_upper)
        cv2.destroyWindow("BLUE ROI")

    if green_lower is not None:
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        #cv2.imshow("Green Mask", green_mask)#

    if blue_lower is not None:
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        #cv2.imshow("Blue Mask", blue_mask)#

    def count(mask, color):
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = 0
        for cnt in contours:
            if cv2.contourArea(cnt) > 300:
                c += 1
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(display, (x,y), (x+w,y+h), color, 2)
        return c

    if green_lower is not None:
        gcount = count(green_mask, (0,255,0))
        cv2.putText(display, f"Green: {gcount}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    if blue_lower is not None:
        bcount = count(blue_mask, (255,0,0))
        cv2.putText(display, f"Blue: {bcount}", (10,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    cv2.imshow("Live Detection", display)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
