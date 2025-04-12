import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Initialize the hand detector with MediaPipe
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def find_hands(self, img, draw=True):
        """
        Find hands in an image and return the processed image and results
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        self.results = self.hands.process(img_rgb)
        
        # Draw hand landmarks if hands are detected and draw is True
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return img
    
    def find_position(self, img, hand_number=0):
        """
        Find the position of hand landmarks
        Returns a list of [id, x, y] for each landmark
        """
        landmark_list = []
        
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_number:
                hand = self.results.multi_hand_landmarks[hand_number]
                
                h, w, c = img.shape
                for id, lm in enumerate(hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, cx, cy])
        
        return landmark_list
    
    def get_gesture(self, landmark_list):
        """
        Determine the gesture (Rock, Paper, Scissors) based on the hand landmarks
        """
        if not landmark_list:
            return None
        
        # Check if we have enough landmarks
        if len(landmark_list) < 21:
            return None
        
        # Extract useful landmarks
        thumb_tip = landmark_list[4]
        index_tip = landmark_list[8]
        middle_tip = landmark_list[12]
        ring_tip = landmark_list[16]
        pinky_tip = landmark_list[20]
        
        wrist = landmark_list[0]
        thumb_mcp = landmark_list[2]
        index_mcp = landmark_list[5]
        middle_mcp = landmark_list[9]
        ring_mcp = landmark_list[13]
        pinky_mcp = landmark_list[17]
        
        # Calculate distances and angles for gesture recognition
        # Distance between fingertips and MCPs
        distances = []
        for tip, mcp in zip([thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip],
                           [thumb_mcp, index_mcp, middle_mcp, ring_mcp, pinky_mcp]):
            # Calculate Euclidean distance
            distance = np.sqrt((tip[1] - mcp[1])**2 + (tip[2] - mcp[2])**2)
            distances.append(distance)
        
        # Normalize distances by the distance from wrist to middle_mcp
        # to account for different hand sizes and distances from camera
        base_distance = np.sqrt((wrist[1] - middle_mcp[1])**2 + (wrist[2] - middle_mcp[2])**2)
        if base_distance > 0:
            normalized_distances = [d / base_distance for d in distances]
        else:
            normalized_distances = distances
        
        # Recognize gestures
        # Rock: All fingers are curled (low normalized distances)
        # Paper: All fingers are extended (high normalized distances)
        # Scissors: Only index and middle fingers are extended
        
        # Threshold for extended finger (can be adjusted)
        threshold = 0.4
        
        is_finger_extended = [d > threshold for d in normalized_distances]
        
        # Rock - all fingers curled (fist)
        if sum(is_finger_extended) <= 1:  # Thumb might appear extended in some fist positions
            return "rock"
        
        # Scissors - index and middle extended, others curled
        if (is_finger_extended[1] and is_finger_extended[2] and 
            not is_finger_extended[3] and not is_finger_extended[4]):
            return "scissors"
        
        # Paper - all fingers extended
        if sum(is_finger_extended) >= 4:  # Allow one finger to be slightly curled
            return "paper"
        
        # Default if no clear gesture is detected
        return None
    
    def get_quadrant(self, landmark_list, img_shape):
        """
        Determine which quadrant the hand is in
        Returns 0, 1, 2, or 3 for top-left, top-right, bottom-left, bottom-right
        """
        if not landmark_list:
            return None
        
        # Use the wrist position to determine quadrant
        wrist = landmark_list[0]
        h, w = img_shape[:2]
        
        x, y = wrist[1], wrist[2]
        
        # Determine quadrant
        if x < w//2 and y < h//2:
            return 0  # Top-left
        elif x >= w//2 and y < h//2:
            return 1  # Top-right
        elif x < w//2 and y >= h//2:
            return 2  # Bottom-left
        else:
            return 3  # Bottom-right