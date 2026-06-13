import cv2
from ultralytics import YOLO

model = YOLO(
    r"C:\Users\Lenovo\Desktop\final crab-.yolov8\runs\detect\train\weights\best.pt"
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("cannot open camera")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("failed to grab frame")
        break

    results = model(
        frame,
        conf=0.65,
        classes=[2],   
        verbose=False
    )

    # Count detections
    num_crabs = len(results[0].boxes)

    # Draw boxes
    frame_with_boxes = results[0].plot()

    cv2.imshow("crab detection", frame_with_boxes)

    print(f"green crabs detected: {num_crabs}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()