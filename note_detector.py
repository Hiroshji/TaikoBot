"""
Note detection module for Taiko Bot
Detects different types of notes using computer vision
"""

import cv2
import numpy as np
from collections import deque


class NoteDetector:
    def __init__(self, config):
        self.config = config
        self.previous_notes = deque(maxlen=10)  # Track previous detections
        self.note_id_counter = 0
        
    def detect_notes(self, frame):
        """Detect all notes in the current frame"""
        notes = []
        
        # Extract detection area from frame
        x, y = self.config.DETECTION_AREA['x'], self.config.DETECTION_AREA['y']
        w, h = self.config.DETECTION_AREA['width'], self.config.DETECTION_AREA['height']
        detection_frame = frame[y:y+h, x:x+w]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2HSV)
        
        # Detect Don (Red) notes
        don_notes = self._detect_color_notes(hsv, detection_frame, 
                                             self.config.DON_COLOR_LOWER,
                                             self.config.DON_COLOR_UPPER,
                                             'don', x, y)
        notes.extend(don_notes)
        
        # Detect Ka (Blue) notes
        ka_notes = self._detect_color_notes(hsv, detection_frame,
                                            self.config.KA_COLOR_LOWER,
                                            self.config.KA_COLOR_UPPER,
                                            'ka', x, y)
        notes.extend(ka_notes)
        
        # Detect Drumroll (Yellow) notes
        drumroll_notes = self._detect_color_notes(hsv, detection_frame,
                                                  self.config.DRUMROLL_COLOR_LOWER,
                                                  self.config.DRUMROLL_COLOR_UPPER,
                                                  'drumroll', x, y)
        notes.extend(drumroll_notes)
        
        # Store notes for prediction
        self.previous_notes.append(notes)
        
        return notes
    
    def _detect_color_notes(self, hsv, frame, lower_bound, upper_bound, note_type, offset_x, offset_y):
        """Detect notes of a specific color"""
        notes = []
        
        # Create mask for the color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones(self.config.MORPHOLOGY_KERNEL, np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Apply Gaussian blur to smooth edges
        mask = cv2.GaussianBlur(mask, self.config.BLUR_KERNEL, 0)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if self.config.MIN_NOTE_AREA < area < self.config.MAX_NOTE_AREA:
                # Get moments for more accurate centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"]) + offset_x
                    center_y = int(M["m01"] / M["m00"]) + offset_y
                else:
                    x, y, w, h = cv2.boundingRect(contour)
                    center_x = x + w // 2 + offset_x
                    center_y = y + h // 2 + offset_y
                
                # Calculate circularity to filter out non-circular shapes
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Accept both circular and slightly oval shapes
                if circularity > 0.4:
                    notes.append({
                        'type': note_type,
                        'position': (center_x, center_y),
                        'area': area,
                        'circularity': circularity,
                        'id': self.note_id_counter
                    })
                    self.note_id_counter += 1
        
        return notes
    
    def predict_note_position(self, note):
        """Predict where the note will be in the next frame(s)"""
        if not self.config.ENABLE_PREDICTION:
            return note['position']
        
        # Simple linear prediction based on estimated speed
        current_x, current_y = note['position']
        
        # Notes typically move from right to left
        predicted_x = current_x - (self.config.NOTE_SPEED_ESTIMATE * self.config.PREDICTION_FRAMES)
        predicted_y = current_y
        
        return (int(predicted_x), int(predicted_y))
    
    def draw_detections(self, frame, notes):
        """Draw detected notes on the frame for debugging"""
        for note in notes:
            x, y = note['position']
            color = self._get_note_color(note['type'])
            
            # Draw circle at note position
            cv2.circle(frame, (x, y), 15, color, 2)
            
            # Draw note type text
            cv2.putText(frame, note['type'].upper(), (x - 20, y - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw prediction if enabled
            if self.config.ENABLE_PREDICTION:
                pred_x, pred_y = self.predict_note_position(note)
                cv2.circle(frame, (pred_x, pred_y), 10, color, 1)
                cv2.line(frame, (x, y), (pred_x, pred_y), color, 1)
        
        return frame
    
    def _get_note_color(self, note_type):
        """Get BGR color for visualization based on note type"""
        colors = {
            'don': (0, 0, 255),      # Red
            'ka': (255, 0, 0),       # Blue
            'drumroll': (0, 255, 255) # Yellow
        }
        return colors.get(note_type, (255, 255, 255))
