import cv2
import numpy as np

class UIRenderer:
    def __init__(self):
        """
        Initialize the UI renderer
        """
        # Colors (BGR format)
        self.BLUE = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (0, 0, 255)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (0, 255, 255)
        self.PURPLE = (255, 0, 255)
        
        # Gesture icons (can be replaced with actual images)
        self.gesture_colors = {
            "rock": self.RED,
            "paper": self.GREEN,
            "scissors": self.BLUE,
            None: self.WHITE
        }
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.font_thickness = 2
        
    def draw_quadrants(self, img):
        """
        Draw the four quadrants on the image
        """
        h, w = img.shape[:2]
        
        # Draw dividing lines
        cv2.line(img, (w//2, 0), (w//2, h), self.WHITE, 2)
        cv2.line(img, (0, h//2), (w, h//2), self.WHITE, 2)
        
        # Label the quadrants
        quadrant_labels = ["Q1", "Q2", "Q3", "Q4"]
        positions = [
            (w//4, h//4),  # Q1: Top-left
            (3*w//4, h//4),  # Q2: Top-right
            (w//4, 3*h//4),  # Q3: Bottom-left
            (3*w//4, 3*h//4)  # Q4: Bottom-right
        ]
        
        for label, pos in zip(quadrant_labels, positions):
            cv2.putText(img, label, pos, self.font, self.font_scale, self.YELLOW, self.font_thickness)
        
        return img
    
    def draw_health_bars(self, img, player_health, computer_health):
        """
        Draw health bars for player and computer
        """
        h, w = img.shape[:2]
        bar_h = 30
        bar_w = w - 100
        
        # Player health bar (bottom)
        player_bar_length = int(bar_w * (player_health / 100))
        cv2.rectangle(img, (50, h - 50), (50 + bar_w, h - 50 + bar_h), self.WHITE, 2)
        cv2.rectangle(img, (50, h - 50), (50 + player_bar_length, h - 50 + bar_h), self.GREEN, -1)
        cv2.putText(img, f"Player: {player_health}", (50, h - 60), self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        # Computer health bar (top)
        computer_bar_length = int(bar_w * (computer_health / 100))
        cv2.rectangle(img, (50, 50), (50 + bar_w, 50 + bar_h), self.WHITE, 2)
        cv2.rectangle(img, (50, 50), (50 + computer_bar_length, 50 + bar_h), self.RED, -1)
        cv2.putText(img, f"Computer: {computer_health}", (50, 40), self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        return img
    
    def draw_round_info(self, img, current_round, max_rounds, player_wins, computer_wins):
        """
        Draw round information
        """
        h, w = img.shape[:2]
        
        # Draw round counter
        cv2.putText(img, f"Round: {current_round}/{max_rounds}", (w - 200, 40), 
                    self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        # Draw win counter
        cv2.putText(img, f"Player wins: {player_wins}", (w - 200, 70), 
                    self.font, self.font_scale, self.GREEN, self.font_thickness)
        cv2.putText(img, f"Computer wins: {computer_wins}", (w - 200, 100), 
                    self.font, self.font_scale, self.RED, self.font_thickness)
        
        return img
    
    def draw_game_state(self, img, game_state, countdown=None):
        """
        Draw the current game state information
        """
        h, w = img.shape[:2]
        center_pos = (w//2, h//2)
        
        if game_state == "waiting":
            cv2.putText(img, "Press 'SPACE' to start round", 
                       (w//2 - 200, h - 100), self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        elif game_state == "countdown":
            cv2.putText(img, str(countdown), 
                       (center_pos[0] - 20, center_pos[1] + 20), 
                       self.font, 5, self.YELLOW, 5)
            
        elif game_state == "round_end":
            cv2.putText(img, "Round End", 
                       (center_pos[0] - 100, center_pos[1]), 
                       self.font, 2, self.YELLOW, 3)
        
        elif game_state == "game_over":
            cv2.putText(img, "GAME OVER", 
                       (center_pos[0] - 150, center_pos[1]), 
                       self.font, 2, self.RED, 4)
            cv2.putText(img, "Press 'R' to restart", 
                       (center_pos[0] - 150, center_pos[1] + 50), 
                       self.font, 1, self.WHITE, 2)
        
        return img
    
    def draw_player_actions(self, img, player_actions, player_quadrants):
        """
        Draw the player's actions on the screen
        """
        h, w = img.shape[:2]
        quadrant_centers = [
            (w//4, h//4),      # Q0: Top-left
            (3*w//4, h//4),    # Q1: Top-right
            (w//4, 3*h//4),    # Q2: Bottom-left
            (3*w//4, 3*h//4)   # Q3: Bottom-right
        ]
        
        # Highlight quadrants with player actions
        for q in player_quadrants:
            if player_actions[q] is not None:
                # Draw a circle representing the gesture
                color = self.gesture_colors[player_actions[q]]
                cv2.circle(img, quadrant_centers[q], 50, color, -1)
                cv2.circle(img, quadrant_centers[q], 50, self.WHITE, 2)
                
                # Draw gesture name
                cv2.putText(img, player_actions[q], 
                           (quadrant_centers[q][0] - 40, quadrant_centers[q][1] + 5), 
                           self.font, self.font_scale, self.BLACK, self.font_thickness)
        
        return img
    
    def draw_computer_actions(self, img, computer_actions, computer_quadrants, game_state):
        """
        Draw the computer's actions on the screen
        """
        # Only show computer actions when round is ended
        if game_state not in ["round_end", "game_over"]:
            return img
        
        h, w = img.shape[:2]
        quadrant_centers = [
            (w//4, h//4),      # Q0: Top-left
            (3*w//4, h//4),    # Q1: Top-right
            (w//4, 3*h//4),    # Q2: Bottom-left
            (3*w//4, 3*h//4)   # Q3: Bottom-right
        ]
        
        # Draw computer actions
        for q in computer_quadrants:
            if computer_actions[q] is not None:
                # Draw a rectangle representing the gesture
                color = self.gesture_colors[computer_actions[q]]
                cv2.rectangle(img, 
                             (quadrant_centers[q][0] - 40, quadrant_centers[q][1] - 40),
                             (quadrant_centers[q][0] + 40, quadrant_centers[q][1] + 40),
                             color, -1)
                cv2.rectangle(img, 
                             (quadrant_centers[q][0] - 40, quadrant_centers[q][1] - 40),
                             (quadrant_centers[q][0] + 40, quadrant_centers[q][1] + 40),
                             self.WHITE, 2)
                
                # Draw gesture name
                cv2.putText(img, computer_actions[q], 
                           (quadrant_centers[q][0] - 40, quadrant_centers[q][1] + 5), 
                           self.font, self.font_scale, self.BLACK, self.font_thickness)
        
        return img
    
    def draw_damage_indicators(self, img, damage_feedback, show_damage):
        """
        Draw damage indicators when hits occur
        """
        if not show_damage:
            return img
        
        h, w = img.shape[:2]
        
        # Player damage
        if damage_feedback["player"] > 0:
            cv2.putText(img, f"-{damage_feedback['player']}", 
                       (w//2 - 50, h - 150), 
                       self.font, 2, self.RED, 3)
        
        # Computer damage
        if damage_feedback["computer"] > 0:
            cv2.putText(img, f"-{damage_feedback['computer']}", 
                       (w//2 - 50, 150), 
                       self.font, 2, self.GREEN, 3)
        
        return img
    
    def draw_current_gesture(self, img, gesture, hand_quadrant):
        """
        Draw the currently detected gesture (for debugging)
        """
        if gesture is None:
            return img
        
        h, w = img.shape[:2]
        
        # Draw at the bottom right
        cv2.putText(img, f"Gesture: {gesture}", 
                   (30, h - 100), 
                   self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        if hand_quadrant is not None:
            cv2.putText(img, f"Quadrant: {hand_quadrant}", 
                       (30, h - 70), 
                       self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        return img
    
    def draw_gestures_guide(self, img):
        """
        Draw a guide for the gestures
        """
        h, w = img.shape[:2]
        guide_w = 220
        guide_h = 150
        guide_x = w - guide_w - 10
        guide_y = h - guide_h - 10
        
        # Background
        cv2.rectangle(img, 
                     (guide_x, guide_y), 
                     (guide_x + guide_w, guide_y + guide_h), 
                     self.BLACK, -1)
        cv2.rectangle(img, 
                     (guide_x, guide_y), 
                     (guide_x + guide_w, guide_y + guide_h), 
                     self.WHITE, 2)
        
        # Title
        cv2.putText(img, "Gesture Guide", 
                   (guide_x + 10, guide_y + 30), 
                   self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        # Gestures
        y_offset = 60
        gestures = ["rock", "paper", "scissors"]
        for i, gesture in enumerate(gestures):
            color = self.gesture_colors[gesture]
            cv2.circle(img, (guide_x + 30, guide_y + y_offset + i*30), 15, color, -1)
            cv2.putText(img, gesture, 
                       (guide_x + 50, guide_y + y_offset + i*30 + 5), 
                       self.font, self.font_scale, self.WHITE, self.font_thickness)
        
        return img