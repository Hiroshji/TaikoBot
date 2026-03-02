"""
Taiko Bot - Headless Version
Runs completely in background, no window needed - like a macro
"""

import cv2
import numpy as np
import mss
import time
from pynput import keyboard
from config import Config
from note_detector import NoteDetector
from input_controller import InputController


class HeadlessTaikoBot:
    def __init__(self):
        self.config = Config()
        self.note_detector = NoteDetector(self.config)
        self.input_controller = InputController(self.config)
        self.running = False
        self.should_quit = False
        self.listener = None
        self.frame_count = 0
        self.hit_count = 0
        self.last_hit_time = 0
        self.last_hit_positions = []  # Track recent hits to avoid duplicates
        
    def on_key_press(self, key):
        """Global hotkey handler"""
        try:
            if key == keyboard.KeyCode(char='q'):
                self.running = True
                print("\n▶ BOT STARTED")
            
            if key == keyboard.KeyCode(char='w'):
                self.running = False
                print("\n⏸ BOT STOPPED")
            
            if key == keyboard.Key.end:
                self.should_quit = True
                print("\n❌ Quitting bot...")
        except AttributeError:
            pass
    
    def detect_and_hit_notes(self, frame):
        """Detect notes and hit them - continuously"""
        try:
            notes = self.note_detector.detect_notes(frame)
            
            current_time = time.time()
            hit_this_frame = False
            
            for note in notes:
                distance = self.calculate_distance(note['position'], self.config.HIT_ZONE)
                
                # Check if note is in hit zone
                if distance <= self.config.HIT_THRESHOLD:
                    # Check if we haven't recently hit a note at this position
                    is_new_note = True
                    for prev_pos, prev_time in self.last_hit_positions[:]:
                        if self.calculate_distance(note['position'], prev_pos) < 30 and (current_time - prev_time) < 0.2:
                            is_new_note = False
                            break
                    
                    if is_new_note:
                        self.input_controller.hit_note(note['type'])
                        self.hit_count += 1
                        self.last_hit_time = current_time
                        self.last_hit_positions.append((note['position'], current_time))
                        
                        # Keep only recent hits
                        if len(self.last_hit_positions) > 20:
                            self.last_hit_positions.pop(0)
                        
                        hit_this_frame = True
                        
                        if self.config.LOG_HITS:
                            print(f"✓ HIT {note['type'].upper():8} | Total: {self.hit_count:4d} | Dist: {distance:6.1f}px")
            
            return hit_this_frame
        except Exception as e:
            print(f"Error detecting notes: {e}")
            return False
    
    def calculate_distance(self, pos1, pos2):
        """Calculate distance between two points"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def run(self):
        """Main bot loop - completely headless"""
        print("=" * 50)
        print("🥁 TAIKO BOT - HEADLESS MODE")
        print("=" * 50)
        print(f"Screen: {self.config.CAPTURE_REGION['width']}x{self.config.CAPTURE_REGION['height']}")
        print(f"Hit Zone: {self.config.HIT_ZONE}")
        print("\n🎮 CONTROLS (Global Hotkeys - Works Anywhere):")
        print("  Q     - Start Bot")
        print("  W     - Stop Bot")
        print("  END   - Quit\n")
        print("Starting in 5 seconds... Switch to your game!")
        print("=" * 50)
        
        # Countdown
        for i in range(5, 0, -1):
            print(f"  {i}...", end='', flush=True)
            time.sleep(1)
        print("\n")
        
        # Auto-start
        self.running = True
        print("▶ BOT STARTED!\n")
        
        # Start global keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        self.should_quit = False
        start_time = time.time()
        
        with mss.mss() as sct:
            monitor = {
                "top": self.config.CAPTURE_REGION['y'],
                "left": self.config.CAPTURE_REGION['x'],
                "width": self.config.CAPTURE_REGION['width'],
                "height": self.config.CAPTURE_REGION['height']
            }
            
            while not self.should_quit:
                try:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Process if running
                    if self.running:
                        self.detect_and_hit_notes(frame)
                    
                    self.frame_count += 1
                    
                    # Print stats every 5 seconds
                    elapsed = time.time() - start_time
                    if self.frame_count % 300 == 0:  # ~5 sec at 60fps
                        fps = self.frame_count / elapsed if elapsed > 0 else 0
                        status = "▶ RUNNING" if self.running else "⏸ PAUSED"
                        print(f"{status} | FPS: {fps:.1f} | Hits: {self.hit_count}")
                    
                    # Keep it smooth
                    time.sleep(0.001)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(0.1)
        
        # Cleanup
        if self.listener:
            self.listener.stop()
        
        elapsed = time.time() - start_time
        print(f"\n" + "=" * 50)
        print(f"Session ended after {elapsed:.1f} seconds")
        print(f"Total hits: {self.hit_count}")
        print(f"Average FPS: {self.frame_count / elapsed:.1f}")
        print("=" * 50)


if __name__ == "__main__":
    bot = HeadlessTaikoBot()
    bot.run()
