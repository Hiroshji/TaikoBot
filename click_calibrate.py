"""
Click-based calibration tool
Click 5 points on screen and it calculates everything
"""

import cv2
import numpy as np
import mss
import json


class ClickCalibrator:
    def __init__(self):
        self.points = []
        self.point_names = [
            "TOP-LEFT (start of note path)",
            "TOP-RIGHT (end of note path)",
            "BOTTOM-LEFT",
            "BOTTOM-RIGHT",
            "HIT ZONE (left edge of circle)"
        ]
        self.screen_shot = None
        self.original_shot = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 5 and self.screen_shot is not None:
                self.points.append((x, y))
                print(f"✓ Point {len(self.points)}: {self.point_names[len(self.points)-1]} = ({x}, {y})")
                
                # Draw the point
                cv2.circle(self.screen_shot, (x, y), 10, (0, 0, 255), -1)
                cv2.circle(self.screen_shot, (x, y), 12, (0, 255, 0), 2)
                cv2.putText(self.screen_shot, f"P{len(self.points)}", (x + 15, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                if len(self.points) == 5:
                    print("\n✓ All 5 points collected!")
                    print("\nCalculating configuration...")
                    self.calculate_config()
                else:
                    print(f"  Click next point: {self.point_names[len(self.points)]}\n")
    
    def calculate_config(self):
        """Calculate config from the 5 points"""
        p1, p2, p3, p4, p5 = self.points
        
        # Detection area from the 4 corners
        top_left_x = p1[0]
        top_left_y = p1[1]
        top_right_x = p2[0]
        top_right_y = p2[1]
        bottom_left_x = p3[0]
        bottom_left_y = p3[1]
        bottom_right_x = p4[0]
        bottom_right_y = p4[1]
        
        # Calculate detection area - use min/max to handle any order
        x = min(top_left_x, bottom_left_x)
        y = min(top_left_y, top_right_y)
        width = max(top_right_x, bottom_right_x) - x
        height = max(bottom_left_y, bottom_right_y) - y
        
        # Ensure positive dimensions
        if width <= 0:
            width = 200
            print("⚠ Warning: Width was negative, using default 200")
        if height <= 0:
            height = 200
            print("⚠ Warning: Height was negative, using default 200")
        
        # Hit zone - center of the circle
        hit_zone_left = p5[0]  # Left edge of circle
        # Estimate center by adding typical circle radius
        hit_zone_x = hit_zone_left + 50  # Typical radius
        hit_zone_y = y + (height // 2)  # Roughly middle of detection area vertically
        
        config = {
            'CAPTURE_REGION': {
                'x': 0,
                'y': 0,
                'width': 2560,
                'height': 1600
            },
            'DETECTION_AREA': {
                'x': int(x),
                'y': int(y),
                'width': int(width),
                'height': int(height)
            },
            'HIT_ZONE': (int(hit_zone_x), int(hit_zone_y)),
            'HIT_RADIUS': 50,
            'PERFECT_RADIUS': 20,
            'HIT_THRESHOLD': 80
        }
        
        print("\n" + "=" * 60)
        print("CALIBRATION RESULTS:")
        print("=" * 60)
        print(f"Detection Area: X={config['DETECTION_AREA']['x']}, Y={config['DETECTION_AREA']['y']}")
        print(f"               Width={config['DETECTION_AREA']['width']}, Height={config['DETECTION_AREA']['height']}")
        print(f"Hit Zone: {config['HIT_ZONE']}")
        print("=" * 60)
        
        # Save to file
        with open('calibration_points.json', 'w') as f:
            json.dump({
                'raw_points': self.points,
                'point_names': self.point_names,
                'config': config
            }, f, indent=2)
        
        print("\n✓ Saved to calibration_points.json")
        print("\nUpdate config.py with these values:")
        print(f"""
DETECTION_AREA = {{
    'x': {config['DETECTION_AREA']['x']},
    'y': {config['DETECTION_AREA']['y']},
    'width': {config['DETECTION_AREA']['width']},
    'height': {config['DETECTION_AREA']['height']}
}}

HIT_ZONE = {config['HIT_ZONE']}
""")
        
        # Draw the calculated areas on screen
        if self.screen_shot is not None:
            det = config['DETECTION_AREA']
            cv2.rectangle(self.screen_shot, 
                         (det['x'], det['y']),
                         (det['x'] + det['width'], det['y'] + det['height']),
                         (0, 255, 0), 3)
            cv2.circle(self.screen_shot, config['HIT_ZONE'], 50, (255, 0, 0), 2)
        
        print("\nPress any key to close and save final image...")
    
    def run(self):
        """Run the calibrator"""
        print("=" * 60)
        print("CLICK CALIBRATOR")
        print("=" * 60)
        print("\nPrepare your game screen...")
        
        import time
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        print("\nCapturing screen...")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Main monitor
            screenshot = sct.grab(monitor)
            self.original_shot = np.array(screenshot)
            self.original_shot = cv2.cvtColor(self.original_shot, cv2.COLOR_BGRA2BGR)
            
            # Ensure we have a valid copy
            if self.original_shot is not None:
                self.screen_shot = self.original_shot.copy()
            else:
                print("Error: Failed to capture screen")
                return
        
        print(f"Screen size: {self.screen_shot.shape[1]}x{self.screen_shot.shape[0]}")
        print("\nClick 5 points in this order:")
        for i, name in enumerate(self.point_names, 1):
            print(f"{i}. {name}")
        
        print(f"\nClick first point: {self.point_names[0]}\n")
        
        # Create window and set mouse callback
        cv2.namedWindow('Click to Calibrate')
        cv2.setMouseCallback('Click to Calibrate', self.mouse_callback)
        
        if self.screen_shot is not None:
            while True:
                cv2.imshow('Click to Calibrate', self.screen_shot)
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                
                if len(self.points) == 5:
                    break
            
            # Save final image
            cv2.imwrite('calibration_visual.png', self.screen_shot)
            print("\n✓ Saved calibration_visual.png")
        
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("Calibration complete!")
        print("=" * 60)


if __name__ == "__main__":
    calibrator = ClickCalibrator()
    calibrator.run()
