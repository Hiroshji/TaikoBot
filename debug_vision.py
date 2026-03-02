"""
Debug tool to visualize what the bot sees
Shows the capture area, detection area, and hit zone
"""

import cv2
import numpy as np
import mss
from config import Config


def debug_vision():
    """Show what the bot is actually looking at"""
    config = Config()
    
    print("Debug Vision Tool")
    print("=" * 50)
    print(f"Capture Region: {config.CAPTURE_REGION}")
    print(f"Detection Area: {config.DETECTION_AREA}")
    print(f"Hit Zone: {config.HIT_ZONE}")
    print("=" * 50)
    print("Press SPACE to capture and save frame")
    print("Press 'q' to quit")
    print()
    
    frame_count = 0
    
    with mss.mss() as sct:
        monitor = {
            "top": config.CAPTURE_REGION['y'],
            "left": config.CAPTURE_REGION['x'],
            "width": config.CAPTURE_REGION['width'],
            "height": config.CAPTURE_REGION['height']
        }
        
        while True:
            # Capture full region
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Resize for viewing
            display = cv2.resize(frame, (800, 600))
            scale_x = frame.shape[1] / display.shape[1]
            scale_y = frame.shape[0] / display.shape[0]
            
            # Draw detection area (scaled for display)
            det = config.DETECTION_AREA
            x1 = int(det['x'] / scale_x)
            y1 = int(det['y'] / scale_y)
            x2 = int((det['x'] + det['width']) / scale_x)
            y2 = int((det['y'] + det['height']) / scale_y)
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 255), 3)  # Yellow
            cv2.putText(display, "DETECTION AREA", (x1 + 5, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Draw hit zone (scaled for display)
            hit_x = int(config.HIT_ZONE[0] / scale_x)
            hit_y = int(config.HIT_ZONE[1] / scale_y)
            cv2.circle(display, (hit_x, hit_y), 30, (0, 255, 0), 3)  # Green
            cv2.circle(display, (hit_x, hit_y), 10, (255, 0, 0), 2)  # Blue center
            cv2.putText(display, "HIT ZONE", (hit_x - 40, hit_y - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('Bot Vision Debug', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                frame_count += 1
                filename = f'debug_frame_{frame_count}.png'
                cv2.imwrite(filename, frame)
                print(f"✓ Saved {filename} (full resolution)")
                cv2.imwrite(f'debug_frame_{frame_count}_display.png', display)
                print(f"✓ Saved debug_frame_{frame_count}_display.png (resized)")
    
    cv2.destroyAllWindows()
    print("Debug tool closed")


if __name__ == "__main__":
    debug_vision()
