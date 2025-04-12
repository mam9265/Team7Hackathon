
import cv2
import time
import numpy as np
from hand_detector import HandDetector
from game_logic import BoxingGame
from ui_renderer import UIRenderer
from boxing_viewer import BoxingViewer

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width
    cap.set(4, 720)   # Height
    
    # Initialize detector, game, and renderer
    detector = HandDetector(min_detection_confidence=0.7)
    game = BoxingGame()
    ui = UIRenderer()
    
    # Initialize the boxing viewer in a separate window
    viewer = BoxingViewer(width=800, height=600)
    viewer.start()
    
    # Main loop
    while True:
        # Get image from camera
        success, img = cap.read()
        if not success:
            print("Failed to get frame from camera")
            break
            
        # Flip image for selfie view
        img = cv2.flip(img, 1)
        

          # Draw boxing ring background
        

        # Find hands
        img = detector.find_hands(img, draw=False)
        
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
        
        # Extract hand position and gesture data for the viewer and game
        glove_positions = []
        glove_gestures = []
        
       # Process gestures if game is in playing state
        if game.game_state == "playing":
            for i, lm_list in enumerate(hands):
                if lm_list:
                    # Get gesture and quadrant
                    gesture = detector.get_gesture(lm_list)
                    quadrant = detector.get_quadrant(lm_list, img.shape)
                    
                    # Register player action if we have a valid gesture and quadrant
                    if gesture is not None and quadrant is not None:
                        # Use the game's register_player_action method which now includes the delay validation
                        game.register_player_action(quadrant, gesture)
                    
                    # Draw current gesture for debugging
                    img = ui.draw_current_gesture(img, gesture, quadrant)
                    
                    # Add hand data for the viewer
                    if len(lm_list) >= 9:  # Make sure we have at least the palm landmark
                        # Use the palm center for positioning the glove
                        palm_x = (lm_list[0][1] + lm_list[9][1]) // 2
                        palm_y = (lm_list[0][2] + lm_list[9][2]) // 2
                        
                        # Rescale coordinates to viewer dimensions
                        viewer_x = int(palm_x * viewer.width / img.shape[1])
                        viewer_y = int(palm_y * viewer.height / img.shape[0])
                        
                        glove_positions.append((viewer_x, viewer_y))
                        glove_gestures.append(gesture)
                else:
                    # Add placeholders if hand not detected
                    glove_positions.append(None)
                    glove_gestures.append(None)
        
        # Use frozen gesture data if round has ended
        if game.game_state == "round_end" and game.frozen_gestures:
            viewer.update_glove_data(game.frozen_positions, game.frozen_gestures, display_duration=5)
        else:
            # Update the viewer with current hand data
            viewer.update_glove_data(glove_positions, glove_gestures)
        
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
    viewer.stop()  # Stop the boxing viewer thread
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()