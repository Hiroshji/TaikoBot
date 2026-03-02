"""
Input controller for Taiko Bot
Simulates keyboard inputs to play the game
"""

import time
import random
from pynput.keyboard import Key, Controller


class InputController:
    def __init__(self, config):
        self.config = config
        self.keyboard = Controller()
        self.last_hit_time = 0
        self.last_key_used = {'don': 0, 'ka': 0}
        self.drumroll_active = False
        self.drumroll_thread = None
        
    def hit_note(self, note_type):
        """Hit a note based on its type"""
        current_time = time.time()
        
        # Add input delay if configured
        if self.config.INPUT_DELAY > 0:
            time.sleep(self.config.INPUT_DELAY)
        
        if note_type == 'don':
            self._hit_don()
        elif note_type == 'ka':
            self._hit_ka()
        elif note_type == 'drumroll':
            self._hit_drumroll()
        
        self.last_hit_time = current_time
        
        if self.config.LOG_HITS:
            print(f"Hit {note_type.upper()} at {current_time:.3f}")
    
    def _hit_don(self):
        """Hit a red note (center drum)"""
        # Alternate between keys for more natural play
        key = self.config.DON_KEYS[self.last_key_used['don'] % len(self.config.DON_KEYS)]
        self.last_key_used['don'] += 1
        
        self._press_key(key)
    
    def _hit_ka(self):
        """Hit a blue note (rim)"""
        # Alternate between keys for more natural play
        key = self.config.KA_KEYS[self.last_key_used['ka'] % len(self.config.KA_KEYS)]
        self.last_key_used['ka'] += 1
        
        self._press_key(key)
    
    def _hit_drumroll(self):
        """Hit a drumroll note (rapid hits)"""
        # For drumrolls, alternate between don keys rapidly
        key = self.config.DON_KEYS[self.last_key_used['don'] % len(self.config.DON_KEYS)]
        self.last_key_used['don'] += 1
        
        self._press_key(key, duration=0.02)  # Shorter press for rolls
    
    def _press_key(self, key, duration=None):
        """Press and release a key"""
        if duration is None:
            duration = self.config.HOLD_DURATION
        
        try:
            self.keyboard.press(key)
            time.sleep(duration)
            self.keyboard.release(key)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
    
    def rapid_fire(self, note_type='don', duration=1.0, hits_per_second=16):
        """Rapid fire hits for drumrolls"""
        end_time = time.time() + duration
        delay = 1.0 / hits_per_second
        
        while time.time() < end_time:
            if note_type == 'don':
                self._hit_don()
            elif note_type == 'ka':
                self._hit_ka()
            time.sleep(delay)
    
    def reset(self):
        """Reset controller state"""
        self.last_hit_time = 0
        self.last_key_used = {'don': 0, 'ka': 0}
        self.drumroll_active = False
