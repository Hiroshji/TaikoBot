"""
Calibration utility for Taiko Bot
Helps you set up the correct capture region, hit zone, and color ranges
"""

import cv2
import numpy as np
import mss
import json


class Calibrator:
    def __init__(self):
        self.capture_region = {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}
        self.hit_zone = (960, 550)
        self.detection_area = {'x': 400, 'y': 400, 'width': 1200, 'height': 300}
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.calibration_mode = 'capture'  # 'capture', 'hit_zone', 'detection'
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selecting = True
            self.selection_start = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selecting:
                self.selection_end = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.selecting = False
            self.selection_end = (x, y)
            self.process_selection()
    
    def process_selection(self):
        """Process the selected area based on current mode"""
        if self.selection_start is None or self.selection_end is None:
            return
        
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        
        # Ensure x1 < x2 and y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        if self.calibration_mode == 'detection':
            self.detection_area = {
                'x': x1,
                'y': y1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            print(f"Detection area set: {self.detection_area}")
        elif self.calibration_mode == 'hit_zone':
            # Set hit zone at selection center
            self.hit_zone = ((x1 + x2) // 2, (y1 + y2) // 2)
            print(f"Hit zone set: {self.hit_zone}")
    
    def run(self):
        """Run the calibration tool"""
        print("=== Taiko Bot Calibration Tool ===")
        print("\nInstructions:")
        print("1. Start your game and position it on screen")
        print("2. Press '1' to select DETECTION AREA (where notes move)")
        print("3. Press '2' to select HIT ZONE (where you hit notes)")
        print("4. Press '3' to test COLOR DETECTION")
        print("5. Press 's' to SAVE configuration")
        print("6. Press 'q' to QUIT")
        print("\nFor selections: Click and drag to select area")
        
        with mss.mss() as sct:
            cv2.namedWindow('Calibration')
            cv2.setMouseCallback('Calibration', self.mouse_callback)
            
            while True:
                # Capture full screen or current region
                monitor = {
                    "top": self.capture_region['y'],
                    "left": self.capture_region['x'],
                    "width": self.capture_region['width'],
                    "height": self.capture_region['height']
                }
                
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Draw current selections
                overlay = frame.copy()
                
                # Draw detection area
                x1 = self.detection_area['x']
                y1 = self.detection_area['y']
                x2 = x1 + self.detection_area['width']
                y2 = y1 + self.detection_area['height']
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(overlay, "Detection Area", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Draw hit zone
                cv2.circle(overlay, self.hit_zone, 50, (0, 255, 0), 3)
                cv2.circle(overlay, self.hit_zone, 20, (255, 0, 0), 2)
                cv2.putText(overlay, "Hit Zone", (self.hit_zone[0] - 40, self.hit_zone[1] - 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Draw current selection
                if self.selecting and self.selection_start and self.selection_end:
                    cv2.rectangle(overlay, self.selection_start, self.selection_end, (0, 0, 255), 2)
                
                # Blend overlay
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                # Draw instructions
                mode_text = f"Mode: {self.calibration_mode.upper()}"
                cv2.putText(frame, mode_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Calibration', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('1'):
                    self.calibration_mode = 'detection'
                    print("Mode: Select DETECTION AREA - drag to select where notes appear")
                elif key == ord('2'):
                    self.calibration_mode = 'hit_zone'
                    print("Mode: Select HIT ZONE - drag around where you hit notes")
                elif key == ord('3'):
                    self.test_color_detection(frame)
                elif key == ord('s'):
                    self.save_config()
        
        cv2.destroyAllWindows()
    
    def test_color_detection(self, frame):
        """Test color detection on current frame"""
        print("\n=== Color Detection Test ===")
        
        # Extract detection area
        x = self.detection_area['x']
        y = self.detection_area['y']
        w = self.detection_area['width']
        h = self.detection_area['height']
        
        roi = frame[y:y+h, x:x+w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Test red (don) detection
        red_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        red_count = cv2.countNonZero(red_mask)
        
        # Test blue (ka) detection
        blue_mask = cv2.inRange(hsv, np.array([100, 100, 100]), np.array([130, 255, 255]))
        blue_count = cv2.countNonZero(blue_mask)
        
        # Test yellow (drumroll) detection
        yellow_mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))
        yellow_count = cv2.countNonZero(yellow_mask)
        
        print(f"Red (Don) pixels: {red_count}")
        print(f"Blue (Ka) pixels: {blue_count}")
        print(f"Yellow (Drumroll) pixels: {yellow_count}")
        
        # Show masks
        cv2.imshow('Red Detection', red_mask)
        cv2.imshow('Blue Detection', blue_mask)
        cv2.imshow('Yellow Detection', yellow_mask)
        print("Press any key to close detection windows...")
        cv2.waitKey(0)
        cv2.destroyWindow('Red Detection')
        cv2.destroyWindow('Blue Detection')
        cv2.destroyWindow('Yellow Detection')
    
    def save_config(self):
        """Save current calibration to config.py"""
        print("\n=== Saving Configuration ===")
        
        config_data = {
            'CAPTURE_REGION': self.capture_region,
            'DETECTION_AREA': self.detection_area,
            'HIT_ZONE': self.hit_zone,
            'HIT_RADIUS': 50,
            'PERFECT_RADIUS': 20,
            'HIT_THRESHOLD': 80
        }
        
        print(f"Detection Area: {self.detection_area}")
        print(f"Hit Zone: {self.hit_zone}")
        
        # Save to JSON file
        with open('calibration.json', 'w') as f:
            json.dump(config_data, f, indent=4)
        
        print("\nConfiguration saved to 'calibration.json'")
        print("Update config.py with these values manually.")


if __name__ == "__main__":
    calibrator = Calibrator()
    calibrator.run()
