"""
Live debug - shows what colors the bot is detecting in real-time
"""

import cv2
import numpy as np
import mss
import time
from config import Config


def live_debug():
    """Show live detection"""
    config = Config()
    
    print("=" * 60)
    print("LIVE COLOR DETECTION DEBUG")
    print("=" * 60)
    print("This shows what the bot actually sees and detects")
    print("Press 'q' to quit")
    print("=" * 60)
    
    with mss.mss() as sct:
        monitor = {
            "top": config.CAPTURE_REGION['y'],
            "left": config.CAPTURE_REGION['x'],
            "width": config.CAPTURE_REGION['width'],
            "height": config.CAPTURE_REGION['height']
        }
        
        while True:
            # Capture
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Extract detection area
            det = config.DETECTION_AREA
            detection_frame = frame[det['y']:det['y']+det['height'], 
                                   det['x']:det['x']+det['width']]
            
            # Convert to HSV
            hsv = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2HSV)
            
            # Create masks for each color
            red_mask = cv2.inRange(hsv, config.DON_COLOR_LOWER, config.DON_COLOR_UPPER)
            blue_mask = cv2.inRange(hsv, config.KA_COLOR_LOWER, config.KA_COLOR_UPPER)
            yellow_mask = cv2.inRange(hsv, config.DRUMROLL_COLOR_LOWER, config.DRUMROLL_COLOR_UPPER)
            
            # Count pixels
            red_pixels = cv2.countNonZero(red_mask)
            blue_pixels = cv2.countNonZero(blue_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            
            # Draw detection area on main frame
            cv2.rectangle(frame, 
                         (det['x'], det['y']),
                         (det['x'] + det['width'], det['y'] + det['height']),
                         (0, 255, 255), 2)
            
            # Draw hit zone
            cv2.circle(frame, config.HIT_ZONE, config.HIT_RADIUS, (0, 255, 0), 2)
            cv2.circle(frame, config.HIT_ZONE, config.HIT_THRESHOLD, (255, 0, 0), 1)
            
            # Draw pixel counts
            cv2.putText(frame, f"Red: {red_pixels}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Blue: {blue_pixels}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, f"Yellow: {yellow_pixels}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Resize for display
            display = cv2.resize(frame, (1000, 750))
            cv2.imshow('Main View', display)
            
            # Show individual color masks
            red_display = cv2.resize(red_mask, (400, 300))
            blue_display = cv2.resize(blue_mask, (400, 300))
            yellow_display = cv2.resize(yellow_mask, (400, 300))
            
            cv2.imshow('RED Detection', red_display)
            cv2.imshow('BLUE Detection', blue_display)
            cv2.imshow('YELLOW Detection', yellow_display)
            
            # Print if detecting anything significant
            if red_pixels > 100 or blue_pixels > 100 or yellow_pixels > 100:
                print(f"DETECTING: Red={red_pixels:5d} Blue={blue_pixels:5d} Yellow={yellow_pixels:5d}")
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    cv2.destroyAllWindows()
    print("\nDebug closed")


if __name__ == "__main__":
    live_debug()
