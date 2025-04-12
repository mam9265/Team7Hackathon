import cv2
import numpy as np
import os
import time
import threading

class BoxingViewer:
    def __init__(self, width=800, height=600):
        """
        Initialize the boxing viewer window with specified dimensions
        """
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Colors (BGR format)
        self.BLUE = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (0, 0, 255)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (0, 255, 255)
        self.BROWN = (42, 42, 165)
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.font_thickness = 2
        
        # Player glove positions (will be updated in real-time)
        self.glove_positions = []
        self.glove_gestures = []
        
        # For freezing gestures
        self.is_frozen = False
        self.freeze_time = 0
        self.freeze_duration = 3.0  # Default to 3 seconds
        self.frozen_positions = []
        self.frozen_gestures = []
        
        # Gesture completion tracking
        self.both_gestures_detected = False
        self.gesture_complete_time = 0
        
        # Mike Tyson sprite (create a placeholder for now)
        self.tyson_sprite = self._create_tyson_sprite()
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Flag to control the viewer thread
        self.running = False
        self.thread = None
        
    def _create_tyson_sprite(self):
        """
        Create a placeholder for Mike Tyson from Punch Out
        In a real implementation, you would load an actual sprite image
        """
        # Create a basic sprite as a placeholder
        sprite = np.zeros((300, 200, 3), dtype=np.uint8)
        
        # Draw a basic figure (this is just a placeholder)
        # Head
        cv2.circle(sprite, (100, 70), 40, (50, 50, 50), -1)  # Dark skin tone
        cv2.rectangle(sprite, (70, 70), (130, 90), (50, 50, 50), -1)  # Face
        
        # Eyes
        cv2.circle(sprite, (80, 60), 5, self.WHITE, -1)
        cv2.circle(sprite, (120, 60), 5, self.WHITE, -1)
        cv2.circle(sprite, (80, 60), 2, self.BLACK, -1)
        cv2.circle(sprite, (120, 60), 2, self.BLACK, -1)
        
        # Mouth with Tyson's iconic smile
        cv2.ellipse(sprite, (100, 80), (20, 10), 0, 0, 180, self.WHITE, 2)
        
        # Body
        cv2.rectangle(sprite, (60, 110), (140, 220), (30, 30, 140), -1)  # Torso with boxing outfit
        
        # Arms
        cv2.rectangle(sprite, (40, 120), (60, 180), (50, 50, 50), -1)  # Left arm
        cv2.rectangle(sprite, (140, 120), (160, 180), (50, 50, 50), -1)  # Right arm
        
        # Gloves
        cv2.circle(sprite, (30, 180), 20, self.RED, -1)  # Left glove
        cv2.circle(sprite, (170, 180), 20, self.RED, -1)  # Right glove
        
        # Text: "MIKE TYSON"
        cv2.putText(sprite, "MIKE TYSON", (45, 250), self.font, 0.6, self.WHITE, 2)
        cv2.putText(sprite, "PUNCH OUT", (55, 280), self.font, 0.5, self.YELLOW, 1)
        
        return sprite
    
    def draw_boxing_ring(self):
        """
        Draw a boxing ring on the canvas
        """
        # Fill the background
        self.canvas.fill(0)  # Black background
        
        # Draw the canvas/mat
        canvas_color = (214, 231, 245)  # Light beige in BGR
        cv2.rectangle(self.canvas, (50, 50), (self.width-50, self.height-50), canvas_color, -1)
        
        # Draw ring ropes (3 levels)
        rope_y_positions = [100, 180, 260]
        for y_pos in rope_y_positions:
            cv2.line(self.canvas, (80, y_pos), (self.width-80, y_pos), self.BROWN, 8)
            cv2.line(self.canvas, (80, y_pos), (self.width-80, y_pos), self.WHITE, 2)
        
        # Draw ring posts at corners
        post_radius = 15
        post_positions = [
            (80, 100),
            (self.width-80, 100),
            (80, 260),
            (self.width-80, 260)
        ]
        
        for pos in post_positions:
            cv2.circle(self.canvas, pos, post_radius, (0, 0, 100), -1)  # Dark red
            cv2.circle(self.canvas, pos, post_radius, self.BLACK, 2)  # Black outline
        
        # Draw ring mat edge
        cv2.rectangle(self.canvas, (80, 100), (self.width-80, self.height-100), (80, 120, 150), 3)
        
        # Draw center of ring logo/text
        cv2.circle(self.canvas, (self.width//2, self.height//2), 70, (200, 200, 220), -1)
        cv2.circle(self.canvas, (self.width//2, self.height//2), 70, self.BLACK, 2)
        cv2.putText(self.canvas, "BOXING", (self.width//2-60, self.height//2-10), 
                  self.font, 1, self.BLACK, 2)
        cv2.putText(self.canvas, "ARENA", (self.width//2-50, self.height//2+30), 
                  self.font, 1, self.BLACK, 2)
    
    def draw_mike_tyson(self):
        """
        Draw Mike Tyson sprite on the canvas
        """
        # Calculate position to place Mike (centered horizontally, near the top)
        x_offset = (self.width - self.tyson_sprite.shape[1]) // 2
        y_offset = 120  # Position from top
        
        # Create a region of interest (ROI) on the canvas
        roi = self.canvas[y_offset:y_offset+self.tyson_sprite.shape[0], 
                          x_offset:x_offset+self.tyson_sprite.shape[1]]
        
        # Create a mask for non-black pixels in the sprite
        mask = cv2.cvtColor(self.tyson_sprite, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
        
        # Create inverted mask
        mask_inv = cv2.bitwise_not(mask)
        
        # Black out the area of the sprite in ROI
        bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        
        # Take only sprite from sprite image
        fg = cv2.bitwise_and(self.tyson_sprite, self.tyson_sprite, mask=mask)
        
        # Combine the two images
        dst = cv2.add(bg, fg)
        self.canvas[y_offset:y_offset+self.tyson_sprite.shape[0], 
                   x_offset:x_offset+self.tyson_sprite.shape[1]] = dst
    
    def draw_boxing_gloves(self):
        """
        Draw boxing gloves based on current positions and gestures
        """
        with self.lock:
            # Use frozen or regular positions/gestures
            positions = self.frozen_positions if self.is_frozen else self.glove_positions
            gestures = self.frozen_gestures if self.is_frozen else self.glove_gestures
            
            # If frozen, display a message about the frozen state
            
            
            for i, (pos, gesture) in enumerate(zip(positions, gestures)):
                if pos is None or gesture is None:
                    continue
                
                # Color alternates between red and blue for different hands
                color = self.BLUE if i % 2 == 0 else self.RED
                
                # Draw different glove shapes based on gesture
                if gesture == "rock":
                    # Fist-shaped glove
                    cv2.circle(self.canvas, pos, 40, color, -1)
                    cv2.circle(self.canvas, pos, 40, self.BLACK, 2)
                    
                elif gesture == "paper":
                    # Open hand glove
                    # Main palm
                    cv2.ellipse(self.canvas, pos, (35, 45), 0, 0, 360, color, -1)
                    cv2.ellipse(self.canvas, pos, (35, 45), 0, 0, 360, self.BLACK, 2)
                    
                    # Fingers (small circles at the edges)
                    finger_radius = 12
                    finger_positions = [
                        (pos[0] - 25, pos[1] - 40),  # Thumb
                        (pos[0] - 10, pos[1] - 55),  # Index
                        (pos[0] + 5, pos[1] - 60),   # Middle
                        (pos[0] + 20, pos[1] - 55),  # Ring
                        (pos[0] + 35, pos[1] - 45)   # Pinky
                    ]
                    
                    for finger_pos in finger_positions:
                        cv2.circle(self.canvas, finger_pos, finger_radius, color, -1)
                        cv2.circle(self.canvas, finger_pos, finger_radius, self.BLACK, 2)
                    
                elif gesture == "scissors":
                    # Scissors glove (two extended fingers)
                    # Main palm
                    cv2.ellipse(self.canvas, pos, (35, 40), 0, 0, 360, color, -1)
                    cv2.ellipse(self.canvas, pos, (35, 40), 0, 0, 360, self.BLACK, 2)
                    
                    # Two extended fingers
                    finger_positions = [
                        (pos[0] - 10, pos[1] - 55),  # Index
                        (pos[0] + 10, pos[1] - 60)   # Middle
                    ]
                    
                    for finger_pos in finger_positions:
                        cv2.circle(self.canvas, finger_pos, 15, color, -1)
                        cv2.circle(self.canvas, finger_pos, 15, self.BLACK, 2)
    
    def update_glove_data(self, positions, gestures, display_duration=None):
        with self.lock:
            # If a specific display duration is provided, use that
            if display_duration:
                self.freeze_time = time.time()
                self.freeze_duration = display_duration
                self.frozen_positions = positions.copy() if isinstance(positions, list) else []
                self.frozen_gestures = gestures.copy() if isinstance(gestures, list) else []
                self.is_frozen = True
                return
                
            # Check if we're currently frozen
            if self.is_frozen:
                # Check if we should unfreeze
                if time.time() - self.freeze_time >= self.freeze_duration:
                    self.is_frozen = False
                    self.both_gestures_detected = False
                    self.glove_positions = positions
                    self.glove_gestures = gestures
                # Otherwise keep using the frozen positions/gestures
                return
                
            # Check if both hands have valid gestures
            valid_gestures = [gesture for gesture in gestures if gesture in ["rock", "paper", "scissors"]]
            
            # If we have 2 valid gestures, freeze them for 3 seconds
            if len(valid_gestures) >= 2 and not self.both_gestures_detected:
                self.both_gestures_detected = True
                self.gesture_complete_time = time.time()
                self.freeze_time = time.time()
                self.freeze_duration = 3.0  # Keep gestures for 3 seconds
                self.frozen_positions = positions.copy() if isinstance(positions, list) else []
                self.frozen_gestures = gestures.copy() if isinstance(gestures, list) else []
                self.is_frozen = True
            else:
                # Normal update if not frozen and not all gestures detected
                self.glove_positions = positions
                self.glove_gestures = gestures
    
    def start(self):
        """
        Start the viewer thread
        """
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """
        Stop the viewer thread
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _run(self):
        """
        Main loop for the viewer thread
        """
        cv2.namedWindow("Boxing Viewer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Boxing Viewer", self.width, self.height)
        
        while self.running:
            # Draw the boxing ring
            self.draw_boxing_ring()
            
            # Draw Mike Tyson
            self.draw_mike_tyson()
            
            # Draw boxing gloves
            self.draw_boxing_gloves()
            
            # Display the image
            cv2.imshow("Boxing Viewer", self.canvas)
            
            # Check for key press to close window
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
            
            # Control frame rate
            time.sleep(1/30)  # ~30 FPS
        
        cv2.destroyWindow("Boxing Viewer")

# Test function to run the viewer standalone
def test_viewer():
    viewer = BoxingViewer()
    viewer.start()
    
    # Simulate some glove movements
    positions = [(200, 400), (600, 400)]
    gestures = ["rock", "scissors"]
    
    try:
        for _ in range(100):
            # Update positions to simulate movement
            positions[0] = (positions[0][0] + np.random.randint(-10, 11), 
                           positions[0][1] + np.random.randint(-10, 11))
            positions[1] = (positions[1][0] + np.random.randint(-10, 11), 
                           positions[1][1] + np.random.randint(-10, 11))
            
            # Occasionally change gestures
            if np.random.random() < 0.1:
                gestures[0] = np.random.choice(["rock", "paper", "scissors"])
            if np.random.random() < 0.1:
                gestures[1] = np.random.choice(["rock", "paper", "scissors"])
                
            
            time.sleep(0.1)
    finally:
        viewer.stop()

if __name__ == "__main__":
    test_viewer()