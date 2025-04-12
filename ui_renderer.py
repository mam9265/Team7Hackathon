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
        self.BROWN = (42, 42, 165)  # For the boxing ring ropes
        
        # Gesture icons (can be replaced with actual images)
        self.gesture_colors = {
            "rock": self.RED,
            "paper": self.GREEN,
            "scissors": self.BLUE,
            None: self.WHITE
        }

        self.player_gesture_images = {
            "rock": cv2.imread("Assets/Rock (Jab).png", cv2.IMREAD_UNCHANGED),
            "paper": cv2.imread("Assets/Paper (Block).png", cv2.IMREAD_UNCHANGED),
            "scissors": cv2.imread("Assets/Scissors (Fake Out).png", cv2.IMREAD_UNCHANGED),
        }

        self.computer_gesture_images = {
            "rock": cv2.imread("Assets/Op Rock.png", cv2.IMREAD_UNCHANGED),
            "paper": cv2.imread("Assets/Op Paper.png", cv2.IMREAD_UNCHANGED),
            "scissors": cv2.imread("Assets/Op Scissors.png", cv2.IMREAD_UNCHANGED),
        }
        
        # Boxing glove colors
        self.player_glove_color = (0, 0, 255)  # Red in BGR
        self.computer_glove_color = (255, 0, 0)  # Blue in BGR
        
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
    
    def overlay_image(self, background, overlay, position):
        x, y = position
        h, w = overlay.shape[:2]

        if overlay.shape[2] == 4:
            # Split channels
            b, g, r, a = cv2.split(overlay)
            mask = cv2.merge((a, a, a))

            roi = background[y:y+h, x:x+w]
            img1_bg = cv2.bitwise_and(roi, 255 - mask)
            img2_fg = cv2.bitwise_and(overlay[:, :, :3], mask)

            dst = cv2.add(img1_bg, img2_fg)
            background[y:y+h, x:x+w] = dst

    
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
                gesture_img = self.player_gesture_images.get(player_actions[q])
                if gesture_img is not None:
                # Resize image to fit nicely
                    resized = cv2.resize(gesture_img, (100, 100))  # or adjust size as needed
                    top_left = (quadrant_centers[q][0] - 50, quadrant_centers[q][1] - 50)
                    self.overlay_image(img, resized, top_left)
                    # Draw gesture name
                    cv2.putText(img, player_actions[q], 
                           (quadrant_centers[q][0] - 40, quadrant_centers[q][1] + 5), 
                           self.font, self.font_scale, self.WHITE, self.font_thickness)
        
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
                gesture_img = self.computer_gesture_images.get(computer_actions[q])
                if gesture_img is not None:
                    resized = cv2.resize(gesture_img, (100, 100))  # or adjust size as needed
                    top_left = (quadrant_centers[q][0] - 50, quadrant_centers[q][1] - 50)
                    self.overlay_image(img, resized, top_left)
                
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
        
    def draw_boxing_ring(self, img):
        """
        Draw a boxing ring as the background
        """
        h, w = img.shape[:2]
        
        # Create a copy of the original image with reduced opacity
        original = img.copy()
        
        # Draw the ring floor (light canvas color)
        canvas_color = (214, 231, 245)  # Light beige in BGR
        cv2.rectangle(img, (0, 0), (w, h), canvas_color, -1)
        
        # Draw the ring ropes (3 levels)
        rope_positions = [h//6, h//3, h//2]
        for y_pos in rope_positions:
            cv2.line(img, (w//8, y_pos), (7*w//8, y_pos), self.BROWN, 8)
            cv2.line(img, (w//8, y_pos), (7*w//8, y_pos), (255, 255, 255), 2)
            
        # Draw the ring posts (corners)
        post_radius = 15
        post_positions = [
            (w//8, h//6), 
            (7*w//8, h//6),
            (w//8, h//2),
            (7*w//8, h//2)
        ]
        
        for pos in post_positions:
            cv2.circle(img, pos, post_radius, (0, 0, 100), -1)  # Dark red
            cv2.circle(img, pos, post_radius, (0, 0, 0), 2)     # Black outline
            
        # Draw the ring mat edge (where it meets the floor)
        cv2.rectangle(img, (w//8-50, h//6-50), (7*w//8+50, 2*h//3), (80, 120, 150), 3)
        
        # Blend the original image back with reduced opacity to preserve the person
        alpha = 0.3  # The lower the more transparent the ring will be
        cv2.addWeighted(img, alpha, original, 1 - alpha, 0, img)
        
        return img
        
    def draw_cpu_boxer(self, img, game_state, player_health=100, computer_health=100):
        """
        Draw a boxer CPU opponent in the top half of the screen
        """
        h, w = img.shape[:2]
        
        # Only draw detailed opponent during active gameplay
        if game_state not in ["countdown", "playing", "round_end", "game_over"]:
            return img
            
        # Center position for the opponent (upper half of screen)
        center_x = w // 2
        center_y = h // 4
        
        # Draw boxer body
        body_height = h // 5
        
        # Torso (trapezoid)
        torso_top_width = w // 10
        torso_bottom_width = w // 6
        
        torso_points = np.array([
            [center_x - torso_top_width//2, center_y - body_height//3],
            [center_x + torso_top_width//2, center_y - body_height//3],
            [center_x + torso_bottom_width//2, center_y + body_height//2],
            [center_x - torso_bottom_width//2, center_y + body_height//2]
        ], np.int32)
        
        cv2.fillPoly(img, [torso_points], (0, 0, 180))  # Dark red color
        cv2.polylines(img, [torso_points], True, (0, 0, 0), 2)
        
        # Head (circle)
        head_radius = h // 16
        cv2.circle(img, (center_x, center_y - body_height//2), head_radius, (200, 160, 130), -1)
        cv2.circle(img, (center_x, center_y - body_height//2), head_radius, (0, 0, 0), 2)
        
        # Eyes
        eye_radius = head_radius // 5
        left_eye_pos = (center_x - head_radius//2, center_y - body_height//2 - head_radius//5)
        right_eye_pos = (center_x + head_radius//2, center_y - body_height//2 - head_radius//5)
        
        cv2.circle(img, left_eye_pos, eye_radius, (255, 255, 255), -1)
        cv2.circle(img, right_eye_pos, eye_radius, (255, 255, 255), -1)
        cv2.circle(img, (left_eye_pos[0], left_eye_pos[1]), eye_radius//2, (0, 0, 0), -1)
        cv2.circle(img, (right_eye_pos[0], right_eye_pos[1]), eye_radius//2, (0, 0, 0), -1)
        
        # Expression based on game state and health
        if game_state in ["playing", "countdown"]:
            # Neutral expression
            cv2.line(img, 
                    (center_x - head_radius//2, center_y - body_height//2 + head_radius//2),
                    (center_x + head_radius//2, center_y - body_height//2 + head_radius//2),
                    (0, 0, 0), 2)
        elif game_state == "round_end" or game_state == "game_over":
            if player_health > computer_health:
                # Sad expression (downward curve)
                pts = np.array([[center_x - head_radius//2, center_y - body_height//2 + head_radius//3],
                              [center_x, center_y - body_height//2 + head_radius//1.5],
                              [center_x + head_radius//2, center_y - body_height//2 + head_radius//3]], np.int32)
                cv2.polylines(img, [pts], False, (0, 0, 0), 2)
            else:
                # Happy expression (upward curve)
                pts = np.array([[center_x - head_radius//2, center_y - body_height//2 + head_radius//2],
                              [center_x, center_y - body_height//2 + head_radius//4],
                              [center_x + head_radius//2, center_y - body_height//2 + head_radius//2]], np.int32)
                cv2.polylines(img, [pts], False, (0, 0, 0), 2)
        
        return img
        
    def draw_computer_hands(self, img, computer_actions, computer_quadrants, game_state):
        """
        Draw computer hands/gloves based on its actions
        """
        h, w = img.shape[:2]
        quadrant_centers = [
            (w//4, h//4),      # Q0: Top-left
            (3*w//4, h//4),    # Q1: Top-right
            (w//4, 3*h//4),    # Q2: Bottom-left
            (3*w//4, 3*h//4)   # Q3: Bottom-right
        ]
        
        # For non-end states, show the computer's hands in shadow/outline form
        # to represent that they're hidden but there
        if game_state not in ["round_end", "game_over"]:
            for q in computer_quadrants:
                # Draw a ghost/shadow boxing glove
                center = quadrant_centers[q]
                
                # Draw shadow glove
                cv2.circle(img, center, 35, (100, 100, 100, 128), -1)  # Semi-transparent gray
                cv2.circle(img, center, 35, (50, 50, 50), 2)  # Dark outline
                
                # Add question mark to indicate hidden gesture
                cv2.putText(img, "?", 
                          (center[0] - 10, center[1] + 10), 
                          self.font, 1.5, (255, 255, 255), 2)
            return img
        
        # For end states, show the actual computer actions with boxing gloves
        for q in computer_quadrants:
            if computer_actions[q] is not None:
                center = quadrant_centers[q]
                gesture = computer_actions[q]
                
                # Draw the glove based on gesture
                if gesture == "rock":
                    # Fist-shaped glove
                    cv2.circle(img, center, 40, self.computer_glove_color, -1)
                    cv2.circle(img, center, 40, (0, 0, 0), 2)
                    
                    # Add thumb
                    thumb_pos = (center[0] - 25, center[1] - 20)
                    cv2.circle(img, thumb_pos, 15, self.computer_glove_color, -1)
                    cv2.circle(img, thumb_pos, 15, (0, 0, 0), 2)
                    
                elif gesture == "paper":
                    # Open hand glove
                    # Main palm
                    cv2.ellipse(img, center, (35, 45), 0, 0, 360, self.computer_glove_color, -1)
                    cv2.ellipse(img, center, (35, 45), 0, 0, 360, (0, 0, 0), 2)
                    
                    # Fingers (small circles at the edges)
                    finger_radius = 12
                    finger_positions = [
                        (center[0] - 25, center[1] - 40),  # Thumb
                        (center[0] - 10, center[1] - 55),  # Index
                        (center[0] + 5, center[1] - 60),   # Middle
                        (center[0] + 20, center[1] - 55),  # Ring
                        (center[0] + 35, center[1] - 45)   # Pinky
                    ]
                    
                    for pos in finger_positions:
                        cv2.circle(img, pos, finger_radius, self.computer_glove_color, -1)
                        cv2.circle(img, pos, finger_radius, (0, 0, 0), 2)
                    
                elif gesture == "scissors":
                    # Scissors glove (two extended fingers)
                    # Main palm
                    cv2.ellipse(img, center, (35, 40), 0, 0, 360, self.computer_glove_color, -1)
                    cv2.ellipse(img, center, (35, 40), 0, 0, 360, (0, 0, 0), 2)
                    
                    # Two extended fingers
                    finger_positions = [
                        (center[0] - 10, center[1] - 55),  # Index
                        (center[0] + 10, center[1] - 60)   # Middle
                    ]
                    
                    for pos in finger_positions:
                        cv2.circle(img, pos, 15, self.computer_glove_color, -1)
                        cv2.circle(img, pos, 15, (0, 0, 0), 2)
                
                # Draw gesture text
                cv2.putText(img, gesture, 
                          (center[0] - 40, center[1] + 50), 
                          self.font, self.font_scale, self.WHITE, self.font_thickness)
                
        return img
    
    def draw_boxing_gloves(self, img, hands_landmarks):
        """
        Draw boxing gloves over the player's hands
        """
        if not hands_landmarks or len(hands_landmarks) == 0:
            return img
            
        for landmarks in hands_landmarks:
            if not landmarks or len(landmarks) < 21:
                continue
                
            # Get key points for the hand
            wrist = landmarks[0]
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            # Get the center of the hand (approximate)
            palm_center_x = (landmarks[0][1] + landmarks[9][1]) // 2
            palm_center_y = (landmarks[0][2] + landmarks[9][2]) // 2
            palm_center = (palm_center_x, palm_center_y)
            
            # Calculate the bounding box of the hand
            x_coords = [lm[1] for lm in landmarks]
            y_coords = [lm[2] for lm in landmarks]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Determine the hand size
            hand_width = x_max - x_min
            hand_height = y_max - y_min
            glove_size = max(hand_width, hand_height) // 2
            
            # Determine the gesture to draw the appropriate glove shape
            # Use fingertips to palm distances to approximate gesture
            fingertip_dists = []
            for tip in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]:
                dist = np.sqrt((tip[1] - palm_center_x)**2 + (tip[2] - palm_center_y)**2)
                fingertip_dists.append(dist)
            
            avg_dist = sum(fingertip_dists) / len(fingertip_dists)
            extended_fingers = sum(1 for d in fingertip_dists if d > avg_dist * 0.7)
            
            # Draw different glove based on gesture
            if extended_fingers <= 1:  # Rock - closed fist
                # Draw the main glove body
                cv2.circle(img, palm_center, glove_size, self.player_glove_color, -1)
                cv2.circle(img, palm_center, glove_size, (0, 0, 0), 2)
                
                # Add thumb extension to the side
                thumb_direction_x = thumb_tip[1] - wrist[1]
                thumb_direction_y = thumb_tip[2] - wrist[2]
                thumb_len = np.sqrt(thumb_direction_x**2 + thumb_direction_y**2)
                if thumb_len > 0:
                    norm_thumb_x = thumb_direction_x / thumb_len
                    norm_thumb_y = thumb_direction_y / thumb_len
                    thumb_pos = (int(palm_center_x + norm_thumb_x * glove_size * 0.7),
                                int(palm_center_y + norm_thumb_y * glove_size * 0.7))
                    cv2.circle(img, thumb_pos, glove_size // 2, self.player_glove_color, -1)
                    cv2.circle(img, thumb_pos, glove_size // 2, (0, 0, 0), 2)
                
            elif extended_fingers == 2:  # Scissors - two extended fingers
                # Draw palm base
                cv2.circle(img, palm_center, glove_size * 0.8, self.player_glove_color, -1)
                cv2.circle(img, palm_center, glove_size * 0.8, (0, 0, 0), 2)
                
                # Draw extended index and middle fingers as cylinders
                for tip, base in [(index_tip, landmarks[5]), (middle_tip, landmarks[9])]:
                    # Calculate finger direction
                    dir_x = tip[1] - base[1]
                    dir_y = tip[2] - base[2]
                    length = np.sqrt(dir_x**2 + dir_y**2)
                    
                    if length > 0:
                        # Normalize direction
                        norm_x = dir_x / length
                        norm_y = dir_y / length
                        
                        # Calculate perpendicular direction for width
                        perp_x = -norm_y
                        perp_y = norm_x
                        
                        # Finger width
                        width = glove_size // 3
                        
                        # Calculate four points for the finger rectangle
                        pts = np.array([
                            [base[1] + perp_x * width, base[2] + perp_y * width],
                            [base[1] - perp_x * width, base[2] - perp_y * width],
                            [tip[1] - perp_x * width, tip[2] - perp_y * width],
                            [tip[1] + perp_x * width, tip[2] + perp_y * width]
                        ], np.int32)
                        
                        # Draw filled polygon
                        cv2.fillPoly(img, [pts], self.player_glove_color)
                        cv2.polylines(img, [pts], True, (0, 0, 0), 2)
                        
                        # Draw rounded tip
                        cv2.circle(img, (tip[1], tip[2]), width, self.player_glove_color, -1)
                        cv2.circle(img, (tip[1], tip[2]), width, (0, 0, 0), 2)
                
            else:  # Paper - open hand
                # Draw palm
                cv2.ellipse(img, palm_center, (glove_size, glove_size * 1.2), 0, 0, 360, self.player_glove_color, -1)
                cv2.ellipse(img, palm_center, (glove_size, glove_size * 1.2), 0, 0, 360, (0, 0, 0), 2)
                
                # Draw fingers
                for tip, mcp in [(thumb_tip, landmarks[2]), 
                                (index_tip, landmarks[5]), 
                                (middle_tip, landmarks[9]), 
                                (ring_tip, landmarks[13]), 
                                (pinky_tip, landmarks[17])]:
                    # Calculate finger direction
                    dir_x = tip[1] - mcp[1]
                    dir_y = tip[2] - mcp[2]
                    length = np.sqrt(dir_x**2 + dir_y**2)
                    
                    if length > 0:
                        # Draw finger
                        finger_thickness = glove_size // 3
                        cv2.line(img, (mcp[1], mcp[2]), (tip[1], tip[2]), self.player_glove_color, finger_thickness)
                        cv2.circle(img, (tip[1], tip[2]), finger_thickness // 2, self.player_glove_color, -1)
                        cv2.circle(img, (tip[1], tip[2]), finger_thickness // 2, (0, 0, 0), 2)
        
        return img