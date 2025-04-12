import random
import time

class BoxingGame:
    def __init__(self):
        """
        Initialize the boxing game with default values
        """
        # Player and computer health
        self.player_health = 100
        self.computer_health = 100
        
        # State tracking
        self.game_state = "waiting"  # waiting, countdown, playing, round_end, game_over
        self.countdown_start = 0
        self.round_end_time = 0
        
        # Gesture stability tracking
        self.gesture_history = {}  # {quadrant: [(gesture, timestamp)]}
        self.stable_gesture_time = 1.0  # Time in seconds a gesture must be stable
        
        # Action tracking for current exchange
        self.player_actions = {0: None, 1: None, 2: None, 3: None}  # Quadrant: Gesture
        self.computer_actions = {0: None, 1: None, 2: None, 3: None}  # Quadrant: Gesture
        
        # Selected quadrants
        self.player_quadrants = []
        self.computer_quadrants = []
        
        # Damage feedback
        self.damage_feedback = {"player": 0, "computer": 0}
        self.damage_time = 0
        
        # Gesture options
        self.gestures = ["rock", "paper", "scissors"]
        
    def start_exchange(self):
        """
        Start a new exchange by initializing countdown
        """
        self.game_state = "countdown"
        self.countdown_start = time.time()
        
    def update_countdown(self):
        """
        Update the countdown timer and change state if finished
        Returns the current countdown value
        """
        elapsed = time.time() - self.countdown_start
        remaining = 3 - int(elapsed)  # 3 second countdown
        
        if remaining <= 0:
            self.game_state = "playing"
            self.select_computer_actions()
            return "GO!"
        
        return str(remaining)
    
    def select_computer_actions(self):
        """
        Randomly select two quadrants and gestures for the computer
        """
        # Select two unique random quadrants
        self.computer_quadrants = random.sample(range(4), 2)
        
        # Assign random gestures to those quadrants
        for quadrant in self.computer_quadrants:
            self.computer_actions[quadrant] = random.choice(self.gestures)
    
    def register_player_action(self, quadrant, gesture):
        """
        Register a player's action in a specific quadrant after ensuring gesture stability
        """
        if self.game_state == "playing" and gesture is not None:
            current_time = time.time()
            
            # Initialize history for this quadrant if it doesn't exist
            if quadrant not in self.gesture_history:
                self.gesture_history[quadrant] = []
            
            # Add the current gesture with timestamp
            self.gesture_history[quadrant].append((gesture, current_time))
            
            # Clean up old entries (older than 1.5 seconds)
            self.gesture_history[quadrant] = [
                (g, t) for g, t in self.gesture_history[quadrant] 
                if current_time - t < 1.5
            ]
            
            # Check if the gesture has been stable for the required time
            if len(self.gesture_history[quadrant]) >= 2:
                # Get all gestures in the last second
                recent_gestures = [
                    g for g, t in self.gesture_history[quadrant] 
                    if current_time - t <= self.stable_gesture_time
                ]
                
                # Check if all recent gestures are the same
                if len(recent_gestures) >= 2 and all(g == gesture for g in recent_gestures):
                    # If the gesture has been stable for 1 second, register it
                    if quadrant in self.player_quadrants and self.player_actions[quadrant] == gesture:
                        # Already registered this gesture for this quadrant
                        pass
                    else:
                        self.player_actions[quadrant] = gesture
                        
                        # Add to player quadrants if not already there
                        if quadrant not in self.player_quadrants and len(self.player_quadrants) < 2:
                            self.player_quadrants.append(quadrant)
                        
                        # Check if we have 2 player actions to resolve the exchange
                        if len([q for q in self.player_quadrants if self.player_actions[q] is not None]) == 2:
                            self.resolve_exchange()
    
    def resolve_exchange(self):
        """
        Resolve the current exchange based on player and computer actions
        """
        # Save current gesture data for the viewer to display for 5 seconds
        self.frozen_gestures = [] 
        self.frozen_positions = []
        
        player_damage = 0
        computer_damage = 0
        
        # Process each player quadrant
        for player_q in self.player_quadrants:
            player_gesture = self.player_actions[player_q]
            
            # Skip if no gesture was detected
            if player_gesture is None:
                continue
                
            # Check if computer is defending this quadrant
            if player_q in self.computer_quadrants:
                computer_gesture = self.computer_actions[player_q]
                
                # Apply RPS rules
                winner = self.determine_winner(player_gesture, computer_gesture)
                
                if winner == "player":
                    computer_damage += 15  # More damage for winning direct confrontation
                elif winner == "computer":
                    player_damage += 15
                # Tie = no damage
                
            else:
                # Direct hit - no defense
                computer_damage += 10
        
        # Process each computer quadrant for attacks on undefended player quadrants
        for computer_q in self.computer_quadrants:
            if computer_q not in self.player_quadrants:
                player_damage += 10  # Direct hit
        
        # Apply damage
        self.player_health = max(0, self.player_health - player_damage)
        self.computer_health = max(0, self.computer_health - computer_damage)
        
        # Record damage for feedback
        self.damage_feedback["player"] = player_damage
        self.damage_feedback["computer"] = computer_damage
        self.damage_time = time.time()
        
        # Check if game is over due to KO
        if self.player_health == 0 or self.computer_health == 0:
            self.game_state = "game_over"
        else:
            # Set timer for exchange end
            self.game_state = "round_end"
            self.round_end_time = time.time()
        
            # Store final gestures and positions for freezing in the viewer
            self.frozen_gestures = True  
    
    def update_round_end(self):
        """
        Update the exchange end state and prepare for the next exchange
        """
        # Show results for 3 seconds
        if time.time() - self.round_end_time > 3:
            self.prepare_next_exchange()
    
    def prepare_next_exchange(self):
        """
        Prepare for the next exchange
        """
        # Reset for next exchange
        self.player_actions = {0: None, 1: None, 2: None, 3: None}
        self.computer_actions = {0: None, 1: None, 2: None, 3: None}
        self.player_quadrants = []
        self.computer_quadrants = []
        self.game_state = "waiting"
    
    def reset_game(self):
        """
        Reset the entire game
        """
        old_stable_time = self.stable_gesture_time  # Save the stable time setting
        self.__init__()
        self.stable_gesture_time = old_stable_time  # Restore the stable time setting
    
    def determine_winner(self, player_gesture, computer_gesture):
        """
        Determine the winner based on RPS rules
        """
        if player_gesture == computer_gesture:
            return "tie"
        
        # Rock beats Scissors
        if player_gesture == "rock" and computer_gesture == "scissors":
            return "player"
        if computer_gesture == "rock" and player_gesture == "scissors":
            return "computer"
        
        # Scissors beats Paper
        if player_gesture == "scissors" and computer_gesture == "paper":
            return "player"
        if computer_gesture == "scissors" and player_gesture == "paper":
            return "computer"
        
        # Paper beats Rock
        if player_gesture == "paper" and computer_gesture == "rock":
            return "player"
        if computer_gesture == "paper" and player_gesture == "rock":
            return "computer"
            
        # Shouldn't reach here, but just in case
        return "tie"
    
    def should_show_damage(self):
        """
        Check if damage indicators should be shown
        """
        return time.time() - self.damage_time < 1  # Show damage for 1 second