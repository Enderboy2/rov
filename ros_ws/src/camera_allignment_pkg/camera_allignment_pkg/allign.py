import rclpy
from rclpy.node import Node
import cv2
import numpy as np

class CameraAllignmentNode(Node):
    def __init__(self):
        super().__init__('camera_allignment_node')
        self.get_logger().info('Camera Allignment Node Started')

        self.selected = []
        self.lastdirection = "MOVE BACK"
        self.cap = cv2.VideoCapture(1)
        cv2.namedWindow('Camera')
        self.timer = self.create_timer(0.03, self.process_frame)
    def click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.selected) < 2:
            for i, c in enumerate(param):
                if cv2.pointPolygonTest(c, (x, y), False) >= 0:
                    if i not in self.selected:
                        self.selected.append(i)
                    break
    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error('Failed to read frame')
            return
        # BGR to HSV conversion
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # creates the mask
        mask = cv2.inRange(hsv, np.array([100, 50, 50]), np.array([130, 255, 255]))
        #prevent detection of 1 rod as more than 1 by connecting blue areas close to each other together
        kernel = np.ones((15, 15), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        #gets outline of detected shapes
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #removes small shapes
        rods = [c for c in contours if cv2.contourArea(c) > 500]
        cv2.setMouseCallback('Camera', self.click, rods)
        for i, c in enumerate(rods):
            # uses moment to calculate rod center for allignment
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                # if rod is selected shows green coloured circle otherwise yellow
                color = (0, 255, 0) if i in self.selected else (0, 255, 255)
                cv2.circle(frame, (cx, int(M["m01"] / M["m00"])), 8, color, -1)
        if len(self.selected) == 2:
            #check if selected rods still exist
            rod1_visible = self.selected[0] < len(rods)
            rod2_visible = self.selected[1] < len(rods)
            if not rod1_visible or not rod2_visible:
                if rod1_visible and not rod2_visible:
                    # gets x coordinate of visible rod's center and compare if its before or after the frame center to determine movement direction
                    x1 = int(cv2.moments(rods[self.selected[0]])["m10"] / cv2.moments(rods[self.selected[0]])["m00"])
                    if x1 > frame.shape[1] // 2:
                        direction = "MOVE RIGHT"
                        self.lastdirection = direction
                    else:
                        direction = "MOVE LEFT"
                        self.lastdirection = direction
                elif rod2_visible and not rod1_visible:
                    x2 = int(cv2.moments(rods[self.selected[1]])["m10"] / cv2.moments(rods[self.selected[1]])["m00"])
                    if x2 > frame.shape[1] // 2:
                        direction = "MOVE RIGHT"
                        self.lastdirection = direction
                    else:
                        direction = "MOVE LEFT"
                        self.lastdirection = direction
                else:
                    # if both rods are not visible uses the last known direction
                    direction = self.lastdirection
                
                cv2.putText(frame, f"ROD LOST - {direction}!", (30, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                self.get_logger().warn(f'ROD LOST - {direction}!')
            else:
                 #when both are visible gets midpoint of center between 2 rods & calculates difference to reach the center
                x1 = int(cv2.moments(rods[self.selected[0]])["m10"] / cv2.moments(rods[self.selected[0]])["m00"])
                x2 = int(cv2.moments(rods[self.selected[1]])["m10"] / cv2.moments(rods[self.selected[1]])["m00"])
                mid = (x1 + x2) // 2
                off = mid - frame.shape[1] // 2
                #determines direction of movement and allows a 30 pixel difference in either direction to center to be called centered
                text = "CENTERED" if abs(off) < 30 else ("MOVE RIGHT" if off > 0 else "MOVE LEFT")
                cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                self.get_logger().info(f'Alignment: {text}')

        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.destroy_node()
            rclpy.shutdown()
    
    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraAllignmentNode()
    #loop node and cleanup at the end
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
