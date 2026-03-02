"""
Configuration file for Taiko Bot
Adjust these values based on your screen resolution and game window position
"""

import numpy as np


class Config:
    # Screen Capture Settings
    # Adjust these to match your game window position and size
    CAPTURE_REGION = {
        'x': 0,           # Left position of capture area
        'y': 0,           # Top position of capture area
        'width': 2560,    # Width of capture area (adjusted for 2560x1600)
        'height': 1600    # Height of capture area (adjusted for 2560x1600)
    }
    
    # Detection Area (where notes appear and move)
    # This is relative to the CAPTURE_REGION
    DETECTION_AREA = {
        'x': 666,
        'y': 462,
        'width': 1891,
        'height': 200     # Fixed from -3 to reasonable value
    }
    
    # Hit Zone (where notes need to be hit)
    # Position relative to CAPTURE_REGION
    HIT_ZONE = (808, 460)
    HIT_RADIUS = 50         # Radius of hit zone
    PERFECT_RADIUS = 20     # Radius for perfect hits
    HIT_THRESHOLD = 80      # Distance threshold to trigger hit
    
    # Note Detection Settings
    # Color ranges for different note types (HSV format)
    # These are tuned for Taiko no Tatsujin - adjust if needed
    
    # Don (Red notes) - hit with face buttons (F/J keys)
    DON_COLOR_LOWER = np.array([0, 80, 80])
    DON_COLOR_UPPER = np.array([25, 255, 255])
    
    # Ka (Blue notes) - hit with rim (D/K keys)
    KA_COLOR_LOWER = np.array([80, 80, 80])
    KA_COLOR_UPPER = np.array([140, 255, 255])
    
    # Yellow (Drumroll) - rapid hits
    DRUMROLL_COLOR_LOWER = np.array([15, 80, 80])
    DRUMROLL_COLOR_UPPER = np.array([40, 255, 255])
    
    # Note size filters (pixel area)
    MIN_NOTE_AREA = 50       # Very small notes
    MAX_NOTE_AREA = 15000    # Very large notes
    
    # Input Settings
    # Key bindings (adjust to match your game settings)
    DON_KEYS = ['f', 'j']     # Keys for red notes (inner drum)
    KA_KEYS = ['d', 'k']      # Keys for blue notes (rim)
    
    # Timing Settings
    INPUT_DELAY = 0.00        # Delay before hitting (seconds) - adjust for calibration
    HOLD_DURATION = 0.05      # How long to hold key (seconds)
    TARGET_FPS = 60           # Target frames per second
    
    # Detection Sensitivity
    BLUR_KERNEL = (5, 5)      # Gaussian blur kernel size
    MORPHOLOGY_KERNEL = (3, 3) # Morphology operation kernel size
    CONFIDENCE_THRESHOLD = 0.7 # Minimum confidence for detection
    
    # Advanced Settings
    ENABLE_PREDICTION = True   # Enable note position prediction
    PREDICTION_FRAMES = 3      # Number of frames to predict ahead
    NOTE_SPEED_ESTIMATE = 15   # Estimated pixels per frame
    
    # Debug Settings
    SHOW_DEBUG_INFO = True     # Show debug overlay
    SAVE_DETECTIONS = False    # Save detected frames to disk
    LOG_HITS = True            # Log hit timing to console
    
    # Global Hotkey Settings
    GLOBAL_STOP_KEY = 'esc'    # Press ESC to stop/start bot (works from game!)
    WINDOW_WIDTH = 400         # Small monitor window (stays in corner)
    WINDOW_HEIGHT = 300
