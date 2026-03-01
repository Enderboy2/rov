import cv2
from ultralytics import YOLO

model = YOLO(r"C:/Users/noura/OneDrive/Desktop/crab-detection/runs/detect/train/weights/best.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("failed to grab frame")
        break

    results = model(frame, conf=0.65, verbose=False)
    filtered_boxes = []
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        if class_name == "green-european-crab":
            x1, y1, x2, y2 = box.xyxy[0]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            filtered_boxes.append(box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.putText(frame, f"green european crabs detected: {len(filtered_boxes)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("crab detection", frame)
    print(f"green european crabs detected: {len(filtered_boxes)}")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()