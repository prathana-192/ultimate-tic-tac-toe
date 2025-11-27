import copy
from mcts_node import MCTSNode

class MCTS:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, initial_state):
        # 1. Create the root node
        root = MCTSNode(state=initial_state)

        # 2. Run the loop for X iterations
        for _ in range(self.iterations):
            node = root
            
            # Phase 1: Selection
            # Keep going down the tree until we find a node that isn't fully expanded
            # or is terminal (game over)
            while node.is_fully_expanded() and not node.is_terminal_node():
                node = node.best_child()

            # Phase 2: Expansion
            # If we aren't at the end of the game, add a new child node
            if not node.is_terminal_node():
                node = self.expand(node)

            # Phase 3: Simulation
            # Play a random game from this new node to the end
            simulation_result = self.simulate(node)

            # Phase 4: Backpropagation
            # Update the scores all the way back up to the root
            self.backpropagate(node, simulation_result)

        # 3. Choose the best move
        # After thinking, pick the child with the most VISITS (most robust move)
        # We use strict exploitation here (c_param=0)
        best_child = root.best_child(c_param=0.0)
        
        return best_child.parent_action

    def expand(self, node):
        """
        Pick one untried action, create a new child node for it, and return that child.
        """
        action = node.untried_actions.pop()
        
        # We must DEEP COPY the state, otherwise we mess up the main board!
        next_state = copy.deepcopy(node.state)
        next_state.make_move(action)
        
        child_node = MCTSNode(
            state=next_state,
            parent=node,
            parent_action=action
        )
        node.children.append(child_node)
        return child_node

    def simulate(self, node):
        """
        Play randomly until game over.
        Returns:
            1 if Player 1 (AI) wins
            -1 if Player 2 (Opponent) wins
            0 for Draw
        """
        # Create a lightweight copy for simulation
        current_state = copy.deepcopy(node.state)
        
        while not current_state.game_over:
            possible_moves = current_state.get_valid_moves()
            if not possible_moves:
                break
            # Pick random move
            action = node.rollout_policy(possible_moves)
            current_state.make_move(action)
            
        return current_state.winner

    def backpropagate(self, node, result):
        """
        Walk up the tree updating visits and values.
        """
        while node is not None:
            node.visits += 1
            
            # Important: MCTS logic differs slightly depending on perspective.
            # If the result is +1 (Player 1 won), that is GOOD for Player 1 nodes 
            # and BAD for Player 2 nodes.
            # However, usually we just sum the rewards.
            # Since our engine returns 1 or -1, we can just add it.
            
            # Note: If the node represents a state where Player 1 just moved,
            # we want to know if that move led to a Player 1 win.
            if node.state.current_player == -1: 
                # The node state is "Player 2 to move" (meaning Player 1 just moved)
                node.value += result 
            else:
                # The node state is "Player 1 to move" (meaning Player 2 just moved)
                node.value -= result

            node = node.parent