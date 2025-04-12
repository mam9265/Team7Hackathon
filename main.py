import cv2
import time
import numpy as np
from hand_detector import HandDetector
from game_logic import BoxingGame
from ui_renderer import UIRenderer

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width
    cap.set(4, 720)   # Height
    
    # Initialize detector, game, and renderer
    detector = HandDetector(min_detection_confidence=0.7)
    game = BoxingGame()
    ui = UIRenderer()
    
    # Main loop
    while True:
        # Get image from camera
        success, img = cap.read()
        if not success:
            print("Failed to get frame from camera")
            break
            
        # Flip image for selfie view
        img = cv2.flip(img, 1)
        
        # Find hands
        img = detector.find_hands(img)
        
        # Get landmark positions for both hands
        lm_list1 = detector.find_position(img, hand_number=0)
        lm_list2 = detector.find_position(img, hand_number=1)
        
        # Process each hand
        hands = [lm_list1, lm_list2]
        
        # Draw quadrants
        img = ui.draw_quadrants(img)
        
        # Draw health bars
        img = ui.draw_health_bars(img, game.player_health, game.computer_health)
        
        # Draw round info
        img = ui.draw_round_info(img, game.current_round, game.max_rounds,
                                game.player_rounds_won, game.computer_rounds_won)
        
        # Process game state
        countdown_value = None
        if game.game_state == "countdown":
            countdown_value = game.update_countdown()
        elif game.game_state == "round_end":
            game.update_round_end()
        
        # Draw game state
        img = ui.draw_game_state(img, game.game_state, countdown_value)
        
        # Process gestures if game is in playing state
        if game.game_state == "playing":
            for i, lm_list in enumerate(hands):
                if lm_list:
                    # Get gesture and quadrant
                    gesture = detector.get_gesture(lm_list)
                    quadrant = detector.get_quadrant(lm_list, img.shape)
                    
                    # Register player action if we have a valid gesture and quadrant
                    if gesture is not None and quadrant is not None:
                        game.register_player_action(quadrant, gesture)
                    
                    # Draw current gesture for debugging
                    img = ui.draw_current_gesture(img, gesture, quadrant)
        
        # Draw player actions
        img = ui.draw_player_actions(img, game.player_actions, game.player_quadrants)
        
        # Draw computer actions
        img = ui.draw_computer_actions(img, game.computer_actions, game.computer_quadrants, game.game_state)
        
        # Draw damage indicators
        img = ui.draw_damage_indicators(img, game.damage_feedback, game.should_show_damage())
        
        # Draw gestures guide
        img = ui.draw_gestures_guide(img)
        
        # Process key events
        key = cv2.waitKey(1) & 0xFF
        
        # Space to start round
        if key == 32 and game.game_state == "waiting":  # Spacebar
            game.start_round()
        
        # R to reset game
        if key == ord('r') and game.game_state == "game_over":
            game.reset_game()
        
        # ESC to quit
        if key == 27:  # ESC
            break
        
        # Display the image
        cv2.imshow("Hand Boxing Game", img)
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()