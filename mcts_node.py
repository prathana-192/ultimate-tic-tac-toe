import numpy as np
import math

class MCTSNode:
    def __init__(self, state, parent=None, parent_action=None):
        self.state = state                  # The board state (UltimateTicTacToe object)
        self.parent = parent                # The parent node
        self.parent_action = parent_action  # The move (0-80) that led to this node
        
        self.children = []                  # List of child Nodes
        self.visits = 0                     # N: How many times visited
        self.value = 0                      # W: Wins/Score accumulation
        
        # Get all legal moves from this state immediately so we know what's possible
        self.untried_actions = state.get_valid_moves()

    def is_fully_expanded(self):
        """Returns True if we have already created children for every possible move."""
        return len(self.untried_actions) == 0

    def is_terminal_node(self):
        """Returns True if the game is over at this node."""
        return self.state.game_over

    def best_child(self, c_param=1.41):
        """
        Selects the best child using the UCB1 formula.
        c_param: Exploration constant (usually sqrt(2) ~ 1.41)
        """
        choices_weights = []
        
        for child in self.children:
            if child.visits == 0:
                # If a child hasn't been visited, give it a huge weight to ensure it gets picked
                weight = 1e9 
            else:
                # Exploitation term (average score)
                exploit = child.value / child.visits
                
                # Exploration term (how curious are we?)
                explore = math.sqrt((2 * math.log(self.visits) / child.visits))
                
                weight = exploit + (c_param * explore)
            
            choices_weights.append(weight)
        
        # Pick the child with the highest UCB score
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        """
        Randomly selects a move for the simulation phase.
        """
        return possible_moves[np.random.randint(len(possible_moves))]