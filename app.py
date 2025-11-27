import streamlit as st
import time
from ultimate_engine import UltimateTicTacToe
from mcts import MCTS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ultimate Tic-Tac-Toe", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@400;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #0a0e27 !important;
        color: #ffffff;
    }
    
    [data-testid="stVerticalBlockContainer"] {
        background: #0a0e27 !important;
    }
    
    .main {
        background: #0a0e27 !important;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .block-container {
        max-width: 1200px;
        padding: 2rem;
        background: #0a0e27 !important;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        border-bottom: 2px solid #00d4ff;
    }
    
    .header-container h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #00d4ff;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    
    /* Status Box */
    .status-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3rem;
        gap: 2rem;
    }
    
    .status-box {
        flex: 1;
        background: linear-gradient(135deg, #00d4ff15 0%, #0099cc15 100%);
        border: 2px solid #00d4ff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        box-shadow: 0 0 20px #00d4ff40;
        letter-spacing: 2px;
    }
    
    .status-box.victory {
        border-color: #00ff00;
        color: #00ff00;
        box-shadow: 0 0 20px #00ff0040;
    }
    
    .status-box.defeat {
        border-color: #ff0000;
        color: #ff0000;
        box-shadow: 0 0 20px #ff000040;
    }
    
    .status-box.draw {
        border-color: #ffaa00;
        color: #ffaa00;
        box-shadow: 0 0 20px #ffaa0040;
    }
    
    /* Game Info */
    .info-box {
        background: #00d4ff10;
        border: 1px solid #00d4ff40;
        padding: 1rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-family: 'Inter', sans-serif;
        color: #00d4ff;
        text-align: center;
        min-width: 200px;
    }
    
    /* Board Container */
    .board-container {
        display: inline-block;
        background: #0f1433;
        padding: 20px;
        border-radius: 16px;
        border: 3px solid #00d4ff;
        box-shadow: 0 0 40px #00d4ff30, inset 0 0 20px #00d4ff10;
        margin: 0 auto;
        display: flex;
        justify-content: center;
    }
    
    .board-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 3rem;
    }
    
    /* Grid Container */
    .grid-container {
        display: inline-block;
        padding: 12px;
        background: #0a0e27;
        border-radius: 8px;
        border: 2px solid #1a2a4a;
        transition: all 0.2s ease;
    }
    
    .grid-container.active {
        border-color: #00d4ff;
        box-shadow: 0 0 15px #00d4ff50, inset 0 0 10px #00d4ff20;
    }
    
    .grid-container.won-x {
        background: #ff000015;
        border-color: #ff0000;
        box-shadow: 0 0 15px #ff000050;
    }
    
    .grid-container.won-o {
        background: #00ff0015;
        border-color: #00ff00;
        box-shadow: 0 0 15px #00ff0050;
    }
    
    .grid-label {
        text-align: center;
        font-size: 0.8rem;
        color: #00d4ff;
        margin-bottom: 8px;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        text-transform: uppercase;
        opacity: 0.7;
    }
    
    .grid-label.active {
        color: #00ff00;
        opacity: 1;
        font-size: 0.9rem;
    }
    
    .grid-label.won {
        font-size: 0.9rem;
        opacity: 1;
    }
    
    /* Cell Styling */
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-size: 32px !important;
        font-weight: bold !important;
        margin: 2px !important;
        padding: 0 !important;
        border-radius: 6px !important;
        border: 2px solid #1a2a4a !important;
        background: #0f1433 !important;
        color: #ffffff !important;
        transition: all 0.15s ease !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    
    .stButton > button:hover:not(:disabled) {
        background: #1a2a4a !important;
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px #00d4ff40 !important;
        transform: scale(1.05) !important;
    }
    
    .stButton > button:disabled {
        cursor: default !important;
        opacity: 0.3 !important;
    }
    
    .stButton > button[kind="primary"] {
        background: #ffaa00 !important;
        border-color: #ffff00 !important;
        color: #000000 !important;
        box-shadow: 0 0 15px #ffaa0060 !important;
    }
    
    /* X and O colors */
    .stButton > button[data-mark="x"] {
        color: #ff0000 !important;
        font-weight: 900 !important;
    }
    
    .stButton > button[data-mark="o"] {
        color: #00ff00 !important;
        font-weight: 900 !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        padding: 2px !important;
    }
    
    .stColumns {
        gap: 0 !important;
    }
    
    /* Controls */
    .controls-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .control-btn {
        padding: 12px 24px;
        font-size: 1rem;
        font-weight: 700;
        border: 2px solid #00d4ff;
        background: #0f1433;
        color: #00d4ff;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .control-btn:hover {
        background: #00d4ff;
        color: #0a0e27;
        box-shadow: 0 0 20px #00d4ff60;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }
    
    /* Hide elements */
    #MainMenu, footer, header {
        display: none !important;
    }
    
    .stMainBlockContainer {
        background: #0a0e27 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'game' not in st.session_state:
    st.session_state.game = UltimateTicTacToe()
    st.session_state.ai = MCTS(iterations=1500) 
    st.session_state.last_move = None
    st.session_state.user_side = 1
    st.session_state.game_over = False
    st.session_state.ai_win_rate = 0

# --- LOGIC HANDLERS ---
def reset_game(user_choice):
    st.session_state.game = UltimateTicTacToe()
    st.session_state.game_over = False
    st.session_state.last_move = None
    st.session_state.user_side = 1 if user_choice == 'X' else -1
    
    if st.session_state.user_side == -1:
        run_ai_turn()

def handle_click(action_idx):
    game = st.session_state.game
    if action_idx in game.get_valid_moves():
        game.make_move(action_idx)
        st.session_state.last_move = action_idx
        
        if game.game_over:
            st.session_state.game_over = True
        else:
            run_ai_turn()

def run_ai_turn():
    game = st.session_state.game
    if game.game_over: return

    with st.spinner("🤖 AI Thinking..."):
        move = st.session_state.ai.search(game)
        game.make_move(move)
        st.session_state.last_move = move
        
        if game.game_over:
            st.session_state.game_over = True

# --- MAIN LAYOUT ---
# Header
st.markdown('<div class="header-container"><h1>⚔️ ULTIMATE TIC-TAC-TOE ⚔️</h1><p class="subtitle">Face the AI in this advanced strategy battle</p></div>', unsafe_allow_html=True)

game = st.session_state.game

# Status Section
col1, col2 = st.columns([2, 1])

with col1:
    status_text = "YOUR TURN"
    status_class = "status-box"
    
    if game.game_over:
        if game.winner == st.session_state.user_side: 
            status_text = "🎉 VICTORY! 🎉"
            status_class = "status-box victory"
        elif game.winner == 0: 
            status_text = "⚖️ DRAW ⚖️"
            status_class = "status-box draw"
        else: 
            status_text = "💀 DEFEAT 💀"
            status_class = "status-box defeat"
    elif game.current_player != st.session_state.user_side:
        status_text = "AI THINKING..."
        status_class = "status-box"
    
    st.markdown(f'<div class="{status_class}">{status_text}</div>', unsafe_allow_html=True)

with col2:
    side_display = "X" if st.session_state.user_side == 1 else "O"
    st.markdown(f'<div class="info-box">YOU ARE: <b>{side_display}</b></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Game Board
valid_moves = game.get_valid_moves()

st.markdown('<div class="board-wrapper"><div class="board-container">', unsafe_allow_html=True)

for big_row in range(3):
    big_cols = st.columns(3, gap="small")
    
    for big_col in range(3):
        grid_idx = big_row * 3 + big_col
        
        with big_cols[big_col]:
            grid_won = game.macro_board[grid_idx]
            is_valid_grid = (game.next_valid_grid == grid_idx or game.next_valid_grid == -1) and not game.game_over
            
            container_class = "grid-container"
            label_class = "grid-label"
            label_text = f"Grid {grid_idx+1}"
            
            if grid_won == 1:
                container_class += " won-x"
                label_text = "✕ WON"
                label_class += " active won"
            elif grid_won == -1:
                container_class += " won-o"
                label_text = "⊙ WON"
                label_class += " active won"
            elif is_valid_grid:
                container_class += " active"
                label_text = "▼ PLAY HERE"
                label_class += " active"
            
            st.markdown(f'<div class="{label_class}">{label_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
            
            for mini_row in range(3):
                mini_cols = st.columns(3, gap="small")
                for mini_col in range(3):
                    local_cell_idx = mini_row * 3 + mini_col
                    global_idx = (grid_idx * 9) + local_cell_idx
                    
                    val = game.board[global_idx]
                    label = ""
                    mark_attr = ""
                    
                    if val == 1: 
                        label = "✕"
                        mark_attr = 'data-mark="x"'
                    elif val == -1: 
                        label = "⊙"
                        mark_attr = 'data-mark="o"'
                    
                    is_last = (global_idx == st.session_state.last_move)
                    btn_type = "primary" if is_last else "secondary"
                    is_valid = global_idx in valid_moves
                    
                    with mini_cols[mini_col]:
                        if st.button(label if label else " ", key=f"c_{global_idx}", type=btn_type, disabled=not is_valid):
                            handle_click(global_idx)
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎮 NEW GAME (Play as X)", use_container_width=True, key="x_btn"):
        reset_game('X')
        st.rerun()

with col2:
    if st.button("🤖 NEW GAME (Play as O)", use_container_width=True, key="o_btn"):
        reset_game('O')
        st.rerun()

with col3:
    if st.button("↻ RESET", use_container_width=True, key="reset_btn"):
        st.session_state.clear()
        st.rerun()