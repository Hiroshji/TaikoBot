"""
Taiko no Tatsujin: Rhythm Festival Bot
Automatically plays the game by detecting notes and hitting them at the right time.
"""

import cv2
import numpy as np
import mss
import time
from collections import deque
import threading
from pynput import keyboard
from config import Config
from note_detector import NoteDetector
from input_controller import InputController


class TaikoBot:
    def __init__(self):
        self.config = Config()
        self.note_detector = NoteDetector(self.config)
        self.input_controller = InputController(self.config)
        self.running = False
        self.fps = 0
        self.frame_times = deque(maxlen=30)
        self.listener = None
        self.should_quit = False
        
    def capture_screen(self, sct, monitor):
        """Capture the game area of the screen"""
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame
    
    def calculate_fps(self):
        """Calculate current FPS"""
        if len(self.frame_times) < 2:
            return 0
        time_diff = self.frame_times[-1] - self.frame_times[0]
        if time_diff == 0:
            return 0
        return len(self.frame_times) / time_diff
    
    def draw_overlay(self, frame):
        """Draw debug information on frame"""
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw status
        status = "RUNNING" if self.running else "STOPPED"
        status_color = (0, 255, 0) if self.running else (0, 0, 255)
        cv2.putText(frame, f"Status: {status}", (10, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Draw hit zone
        hit_zone = self.config.HIT_ZONE
        cv2.circle(frame, hit_zone, self.config.HIT_RADIUS, (0, 255, 0), 3)
        cv2.circle(frame, hit_zone, self.config.PERFECT_RADIUS, (255, 0, 0), 2)
        
        # Draw detection area
        x1, y1 = self.config.DETECTION_AREA['x'], self.config.DETECTION_AREA['y']
        x2, y2 = x1 + self.config.DETECTION_AREA['width'], y1 + self.config.DETECTION_AREA['height']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        
        # Draw instructions
        cv2.putText(frame, "Press ESC to toggle", (10, frame.shape[0] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Press Q to quit", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def process_frame(self, frame):
        """Process a single frame and detect notes"""
        # Detect notes in the frame
        notes = self.note_detector.detect_notes(frame)
        
        # Check if any notes are in the hit zone
        for note in notes:
            distance = self.calculate_distance(note['position'], self.config.HIT_ZONE)
            
            # If note is close enough to hit zone, hit it
            if distance <= self.config.HIT_THRESHOLD:
                self.input_controller.hit_note(note['type'])
                
                if self.config.LOG_HITS:
                    print(f"HIT: {note['type'].upper()} at distance {distance:.1f}")
        
        return frame
    
    def calculate_distance(self, pos1, pos2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def on_key_press(self, key):
        """Global hotkey handler - listens even when game is focused"""
        try:
            # Check for ESC to toggle
            if key == keyboard.Key.esc:
                self.running = not self.running
                status = "STARTED" if self.running else "STOPPED"
                print(f"\n*** Bot {status} ***")
            
            # Check for Q to quit
            if key == keyboard.Key.end:  # Using END key as alternative quit
                self.should_quit = True
                print("\n*** Bot Quitting ***")
        except AttributeError:
            pass
    
    def run(self):
        """Main bot loop"""
        print("Taiko Bot Starting...")
        print(f"Capture Area: {self.config.CAPTURE_REGION}")
        print(f"Hit Zone: {self.config.HIT_ZONE}")
        print("\n=== CONTROLS (GLOBAL HOTKEYS - Works from game!) ===")
        print("Press ESC to START/STOP the bot")
        print("Press END to QUIT")
        print("\n=== AUTO-START ===")
        print("Bot will auto-start in 5 seconds...")
        print("Switch to your game window now!")
        
        # Auto-start countdown
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        self.running = True
        print("\n*** BOT STARTED! ***")
        print("Keep this window visible but in background")
        
        # Start global keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        self.should_quit = False
        
        with mss.mss() as sct:
            monitor = {
                "top": self.config.CAPTURE_REGION['y'],
                "left": self.config.CAPTURE_REGION['x'],
                "width": self.config.CAPTURE_REGION['width'],
                "height": self.config.CAPTURE_REGION['height']
            }
            
            while not self.should_quit:
                start_time = time.time()
                
                # Capture screen
                frame = self.capture_screen(sct, monitor)
                
                # Resize frame for display
                display_frame = cv2.resize(frame, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
                
                # Process frame if bot is running
                if self.running:
                    frame = self.process_frame(frame)
                
                # Draw overlay on original frame
                frame = self.draw_overlay(frame)
                
                # Resize for display
                display_frame = cv2.resize(frame, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
                
                # Calculate FPS
                self.frame_times.append(time.time())
                self.fps = self.calculate_fps()
                
                # Show frame
                cv2.imshow('Taiko Bot Monitor', display_frame)
                
                # Handle local key presses (for the window itself)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.should_quit = True
                
                # Maintain target FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, (1.0 / self.config.TARGET_FPS) - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        # Stop listener
        if self.listener:
            self.listener.stop()
        
        cv2.destroyAllWindows()
        print("Bot stopped.")


if __name__ == "__main__":
    bot = TaikoBot()
    bot.run()
