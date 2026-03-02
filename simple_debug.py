"""
Simple debug - just shows what the bot is capturing
"""

import cv2
import numpy as np
import mss
import os
from config import Config


def simple_debug():
    """Simple debug - capture and show what bot sees"""
    config = Config()
    
    print("\n" + "=" * 60)
    print("SIMPLE DEBUG TOOL")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    print(f"Capture area: X={config.CAPTURE_REGION['x']} Y={config.CAPTURE_REGION['y']}")
    print(f"            Width={config.CAPTURE_REGION['width']} Height={config.CAPTURE_REGION['height']}")
    print(f"Detection area: X={config.DETECTION_AREA['x']} Y={config.DETECTION_AREA['y']}")
    print(f"               Width={config.DETECTION_AREA['width']} Height={config.DETECTION_AREA['height']}")
    print(f"Hit zone: {config.HIT_ZONE}")
    print("=" * 60)
    print("Press SPACEBAR to save screenshot")
    print("Press 'q' to quit")
    print("=" * 60 + "\n")
    
    save_count = 0
    
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
            
            # Draw overlays on original frame
            overlay = frame.copy()
            
            # Draw detection area
            det = config.DETECTION_AREA
            cv2.rectangle(overlay, 
                         (det['x'], det['y']), 
                         (det['x'] + det['width'], det['y'] + det['height']),
                         (0, 255, 255), 3)
            cv2.putText(overlay, "DETECTION AREA", (det['x'], det['y'] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Draw hit zone
            cv2.circle(overlay, config.HIT_ZONE, 50, (0, 255, 0), 3)
            cv2.circle(overlay, config.HIT_ZONE, 20, (255, 0, 0), 3)
            cv2.putText(overlay, "HIT ZONE", (config.HIT_ZONE[0] - 60, config.HIT_ZONE[1] - 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Resize for display
            display = cv2.resize(overlay, (1000, 750))
            
            cv2.imshow('Debug - Press SPACE to save, Q to quit', display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # q or ESC
                print("\n❌ Closing...")
                break
            
            elif key == 32:  # SPACEBAR
                save_count += 1
                full_path = os.path.join(os.getcwd(), f'screenshot_{save_count}.png')
                success = cv2.imwrite(full_path, frame)
                
                if success:
                    print(f"✓ SAVED: {full_path}")
                    print(f"  File size: {os.path.getsize(full_path)} bytes")
                else:
                    print(f"✗ FAILED to save: {full_path}")
    
    cv2.destroyAllWindows()
    print("\n" + "=" * 60)
    print("Debug closed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    simple_debug()
