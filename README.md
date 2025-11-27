# TTT XO // Ultimate Tic-Tac-Toe AI 🤖

**TTT XO** is an advanced implementation of "Ultimate Tic-Tac-Toe" featuring a custom AI agent powered by Monte Carlo Tree Search (MCTS). Unlike standard Minimax algorithms, this agent does not rely on hard-coded heuristics; instead, it learns the best move in real-time by simulating thousands of potential future game outcomes.

The frontend is built with a custom PyGame engine rendered strictly for the web using Streamlit, providing a high-performance, neon-cyberpunk aesthetic.

---

## How to Play
Ultimate Tic-Tac-Toe is a game of *Inception*—a board within a board.

1.  **The Grid:** The game consists of 9 small Tic-Tac-Toe boards arranged in a $3 \times 3$ global grid.
2.  **The Objective:** Win 3 small boards in a row (Horizontally, Vertically, or Diagonally) to win the Global Game.
3.  **The Constraint (Crucial Rule):** You cannot play wherever you want.
    * If X plays in the Top-Right cell of a local board...
    * O is *forced* to play in the Top-Right local board of the global grid.
    * *Exception:* If the target board is already full or won, the player is "sent to jail" and may play anywhere (Free Move).

---

##  Installation & Run

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/prathana-192/ultimate-tic-tac-toe.git](https://github.com/prathana-192/ultimate-tic-tac-toe.git)
    cd ultimate-tic-tac-toe
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the App**
    ```bash
    streamlit run app_pygame.py
    ```

---

##  The AI: How it Works

The "Brain" of this game is not a pre-trained Neural Network. It is a Monte Carlo Tree Search (MCTS) algorithm. This is the same class of algorithm used by DeepMind's AlphaGo (before the neural network integration).

### The Concept
Instead of memorizing every possible state (which is impossible, as Ultimate TTT has roughly $10^{50}$ states), the AI uses probabilistic simulation.

When it is the AI's turn to move:
1.  It looks at the current board.
2.  It creates a "Game Tree" of possible moves.
3.  It plays out 1,200+ random games (simulations) from the current state to the very end of the game.
4.  It tracks which moves led to a Win (+1) and which led to a Loss (-1).
5.  It selects the move with the highest statistical probability of winning.

### The Algorithm Phases
1.  **Selection:** The AI traverses the existing tree using the UCB1 Formula (see Math below) to find the most promising node to explore.
2.  **Expansion:** It adds a new child node (a new potential move) to the tree.
3.  **Simulation (Rollout):** It plays random moves from that new node until the game ends.
4.  **Backpropagation:** It updates the win/loss stats of all nodes along the path back to the root.

---

## 📐 The Math Behind the Magic

The core logic determining "smart" behavior vs. "random" behavior is the Upper Confidence Bound 1 (UCB1) algorithm. This formula solves the Exploration vs. Exploitation dilemma.

* **Exploitation:** "This move worked before, I should do it again."
* **Exploration:** "I haven't tried that move yet, it might be a winning trap."

### The Formula
$$UCB1 = \frac{w_i}{n_i} + C \sqrt{\frac{\ln N}{n_i}}$$

Where:
* $w_i$: Number of wins after the $i$-th move.
* $n_i$: Number of simulations involving the $i$-th move.
* $N$: Total number of simulations run for the parent node.
* $C$: The Exploration Constant (usually $\sqrt{2} \approx 1.41$).

### How the Math works in TTT XO:
1.  **Left Term ($\frac{w_i}{n_i}$):** This is the Win Rate. If a move has a high win rate, this term is large. The AI *exploits* known good moves.
2.  **Right Term ($C \sqrt{\dots}$):** This is the Curiosity Factor. If a move has been visited rarely ($n_i$ is small), this term becomes huge (because we divide by a small number). The AI *explores* the unknown.
3.  As $n_i$ increases (we visit a node more), the uncertainty drops, and the AI relies more on the pure Win Rate.

---

##  Project Structure

* `app_pygame.py` - The Frontend. Handles the Streamlit interface and Headless PyGame rendering.
* `mcts.py` - The Agent. Manages the simulation loop and time constraints.
* `mcts_node.py` - The Data Structure. Represents a state in the decision tree and calculates UCB1.
* `ultimate_engine.py` - The Environment. Enforces the strict rules, constraints, and win checking.

---

##  Tech Stack
* **Python:** Core logic.
* **NumPy:** High-performance matrix operations for the board state.
* **PyGame:** Used in "Headless Mode" to draw pixel-perfect grids and neon effects, converted to images for the web.
* **Streamlit:** The web framework hosting the UI.
* **Streamlit-Image-Coordinates:** Captures user clicks on the PyGame surface.

---

### Author
Built by **Prathana Sharma**.
