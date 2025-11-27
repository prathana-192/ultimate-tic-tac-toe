import random
import time
from ultimate_engine import UltimateTicTacToe
from mcts import MCTS

def run_ai_test():
    game = UltimateTicTacToe()
    ai = MCTS(iterations=1000) # 1000 simulations per move
    
    print("=== AI (Player 1) vs RANDOM (Player -1) ===")
    
    while not game.game_over:
        print(f"\n--- Turn: Player {game.current_player} ---")
        
        if game.current_player == 1:
            # AI Turn
            print("AI is thinking...")
            start_time = time.time()
            move = ai.search(game) # <--- AI DECIDES HERE
            end_time = time.time()
            print(f"AI chose move: {move} (Time: {end_time - start_time:.2f}s)")
        else:
            # Random Turn
            moves = game.get_valid_moves()
            move = random.choice(moves)
            print(f"Random player chose: {move}")
            
        game.make_move(move)
        
        # Optional: Print Macro Board status
        print(f"Macro Board: {game.macro_board}")

    if game.winner == 1:
        print("\nVICTORY: The AI Won!")
    elif game.winner == -1:
        print("\nDEFEAT: Random Player Won (This shouldn't happen often!)")
    else:
        print("\nDRAW!")

if __name__ == "__main__":
    run_ai_test()