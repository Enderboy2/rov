import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import time

class CameraAllignmentNode(Node):
    def __init__(self):
        super().__init__('allign')
        self.get_logger().info('Camera Allignment Node Started')

        self.selected = []
        self.lastdirection = "MOVE BACK"
        self.cap = cv2.VideoCapture(1)
        cv2.namedWindow('Camera')
        self.state = "ALIGNING"
        self.center_start_time = None
        self.required_center_time = 5.0
        self.both_rods_lost_time = None
        self.confirmation_time = 3.0 
        self.timer = self.create_timer(0.03, self.process_frame)
        
    def click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.selected) < 2:
            for i, c in enumerate(param):
                # checks if my click is inside the detected rod shapes
                if cv2.pointPolygonTest(c, (x, y), False) >= 0:
                    if i not in self.selected:
                        self.selected.append(i)
                    break
    
    def process_frame(self):
        ret, frame = self.cap.read()
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
            
            if not rod1_visible and not rod2_visible:
                #checks if line ended or just disappeared due to misallignment
                if self.both_rods_lost_time is None:
                    self.both_rods_lost_time = time.time()
                    self.get_logger().warn('Both rods lost waiting for confirmation')
                
                time_lost = time.time() - self.both_rods_lost_time
                
                if time_lost >= self.confirmation_time:
                    self.state = "COMPLETED"
                    cv2.putText(frame, "MISSION COMPLETE!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    self.get_logger().info('MISSION COMPLETE')
                else:
                    remaining = self.confirmation_time - time_lost
                    cv2.putText(frame, f"Confirming end {remaining:.1f}s", (30, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 3)
                    cv2.putText(frame, f"{self.lastdirection}", (30, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    
            else:
                self.both_rods_lost_time = None
                
                if not rod1_visible or not rod2_visible:
                    if rod1_visible and not rod2_visible:
                        # gets x coordinate of visible rod's center and compare if its before or after the frame center to determine movement direction
                        x1 = int(cv2.moments(rods[self.selected[0]])["m10"] / cv2.moments(rods[self.selected[0]])["m00"])
                        direction = "MOVE RIGHT" if x1 > frame.shape[1] // 2 else "MOVE LEFT"
                        self.lastdirection = direction
                    elif rod2_visible and not rod1_visible:
                        x2 = int(cv2.moments(rods[self.selected[1]])["m10"] / cv2.moments(rods[self.selected[1]])["m00"])
                        direction = "MOVE RIGHT" if x2 > frame.shape[1] // 2 else "MOVE LEFT"
                        self.lastdirection = direction
                    else:
                        # if both rods are not visible uses the last known direction
                        direction = self.lastdirection
                    
                    self.center_start_time = None
                    self.state = "ALIGNING"
                    
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
                    is_centered = abs(off) < 30
                    if is_centered:
                        #if remained centered for 5 seconds start moving forward
                        if self.center_start_time is None:
                            self.center_start_time = time.time()
                        
                        time_centered = time.time() - self.center_start_time
                        
                        if self.state == "ALIGNING":
                            self.state = "WAITING"
                        
                        if self.state == "WAITING":
                            remaining = self.required_center_time - time_centered
                            if remaining > 0:
                                cv2.putText(frame, f"CENTERED - Wait {remaining:.1f}s", (50, 50), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
                                self.get_logger().info(f'Waiting... {remaining:.1f}s remaining')
                            else:
                                self.state = "MOVING_FORWARD"
                                self.get_logger().info('MOVING FORWARD')
                        
                        if self.state == "MOVING_FORWARD":
                            cv2.putText(frame, "MOVING FORWARD - CENTERED", (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                            print("MOVE FORWARD")
                    
                    else:
                        #fixes allignment while moving if missallignment occured
                        direction = "MOVE RIGHT" if off > 0 else "MOVE LEFT"
                        self.center_start_time = None
                        
                        if self.state == "MOVING_FORWARD":
                            cv2.putText(frame, f"MOVING FORWARD + {direction}", (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 165, 0), 3)
                            print(f"MOVE FORWARD + MOVE {direction}")
                        else:
                            self.state = "ALIGNING"
                            cv2.putText(frame, direction, (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
                            self.get_logger().info(f'Aligning: {direction}')
        
        cv2.putText(frame, f"State: {self.state}", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
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
    
    try:
        #loop
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()