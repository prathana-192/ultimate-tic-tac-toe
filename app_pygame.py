import streamlit as st
import pygame
import os
import numpy as np
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
from ultimate_engine import UltimateTicTacToe
from mcts import MCTS

# --- 1. HEADLESS SETUP ---
os.environ["SDL_VIDEODRIVER"] = "dummy"

# --- 2. CONFIG ---
st.set_page_config(page_title="TTT XO", layout="wide", initial_sidebar_state="collapsed")

# GAME DIMENSIONS
# We keep the logical board square to ensure X and O don't look stretched
# But we can resize the display in the column later.
GAME_RES = 600 
CELL_SIZE = GAME_RES // 9
GRID_SIZE = GAME_RES // 3

# CYBERPUNK PALETTE
COLOR_BG = (11, 15, 25)        # Deep Space Blue
COLOR_GRID_THIN = (40, 50, 70) # Faint Grid
COLOR_GRID_THICK = (0, 243, 255)# Neon Cyan
COLOR_X = (255, 46, 80)        # Neon Red
COLOR_O = (0, 243, 255)        # Neon Cyan
COLOR_VALID_ZONE = (20, 30, 50)# Active Zone Highlight
COLOR_LAST_MOVE = (255, 180, 0)# Amber Gold

# --- 3. CUSTOM CSS (THE GAMING LOOK) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

    /* APP BACKGROUND */
    .stApp {
        background-color: #0b0f19;
        color: white;
    }

    /* HEADERS */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #00f3ff, #ff2e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0px;
    }

    /* SCORE CARD */
    .score-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .score-val {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .score-label {
        font-size: 0.8rem;
        color: #888;
        letter-spacing: 1px;
    }

    /* BUTTONS */
    div.stButton > button {
        background-color: transparent;
        border: 2px solid #00f3ff;
        color: #00f3ff;
        font-family: 'Orbitron', sans-serif;
        border-radius: 5px;
        transition: all 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00f3ff;
        color: #000;
        box-shadow: 0 0 15px #00f3ff;
    }
    
    /* REMOVE PADDING */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'game' not in st.session_state:
    st.session_state.game = UltimateTicTacToe()
    st.session_state.ai = MCTS(iterations=1200) # Good balance of speed/skill
    st.session_state.last_move = None
    st.session_state.user_side = 1 
    st.session_state.game_over = False
    # SCOREBOARD
    st.session_state.wins_user = 0
    st.session_state.wins_ai = 0

# --- 5. RENDERER ---
def render_game_image(game, last_move):
    pygame.init()
    surface = pygame.Surface((GAME_RES, GAME_RES))
    
    # Fonts
    font_main = pygame.font.SysFont("arial", int(CELL_SIZE * 0.7), bold=True)
    font_big = pygame.font.SysFont("arial", int(GRID_SIZE * 0.8), bold=True)

    # A. BG
    surface.fill(COLOR_BG)

    # B. ZONES
    for i in range(9):
        r, c = i // 3, i % 3
        rect = (c*GRID_SIZE, r*GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        # Won Grids
        if game.macro_board[i] == 1:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE))
            s.set_alpha(50)
            s.fill(COLOR_X)
            surface.blit(s, (c*GRID_SIZE, r*GRID_SIZE))
        elif game.macro_board[i] == -1:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE))
            s.set_alpha(50)
            s.fill(COLOR_O)
            surface.blit(s, (c*GRID_SIZE, r*GRID_SIZE))
        # Valid Move Zone
        elif (game.next_valid_grid == i or game.next_valid_grid == -1) and not game.game_over:
            pygame.draw.rect(surface, COLOR_VALID_ZONE, rect)
            # Add a glowing border to valid zone
            pygame.draw.rect(surface, (50, 60, 90), rect, 3)

    # C. LAST MOVE HIGHLIGHT
    if last_move is not None:
        g_idx, c_idx = last_move // 9, last_move % 9
        # Calculate Global X/Y
        gx = (g_idx % 3) * 3 + (c_idx % 3)
        gy = (g_idx // 3) * 3 + (c_idx // 3)
        pygame.draw.rect(surface, COLOR_LAST_MOVE, (gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    # D. GRID LINES
    # Thin
    for i in range(1, 9):
        pygame.draw.line(surface, COLOR_GRID_THIN, (i*CELL_SIZE, 0), (i*CELL_SIZE, GAME_RES), 1)
        pygame.draw.line(surface, COLOR_GRID_THIN, (0, i*CELL_SIZE), (GAME_RES, i*CELL_SIZE), 1)
    # Thick (Neon)
    for i in range(1, 3):
        # Glow Effect (Draw multiple lines with decreasing alpha? Pygame is simple, lets just do thick lines)
        pygame.draw.line(surface, COLOR_GRID_THICK, (i*GRID_SIZE, 0), (i*GRID_SIZE, GAME_RES), 4)
        pygame.draw.line(surface, COLOR_GRID_THICK, (0, i*GRID_SIZE), (GAME_RES, i*GRID_SIZE), 4)

    # E. MARKS (X / O)
    for i in range(81):
        if game.board[i] != 0:
            g_idx, c_idx = i // 9, i % 9
            gx = (g_idx % 3) * 3 + (c_idx % 3)
            gy = (g_idx // 3) * 3 + (c_idx // 3)
            
            center = (gx * CELL_SIZE + CELL_SIZE//2, gy * CELL_SIZE + CELL_SIZE//2)
            
            txt = "X" if game.board[i] == 1 else "O"
            col = COLOR_X if game.board[i] == 1 else COLOR_O
            
            # Simple Shadow
            s_surf = font_main.render(txt, True, (0,0,0))
            s_rect = s_surf.get_rect(center=(center[0]+2, center[1]+2))
            surface.blit(s_surf, s_rect)
            
            # Main Text
            t_surf = font_main.render(txt, True, col)
            t_rect = t_surf.get_rect(center=center)
            surface.blit(t_surf, t_rect)

    # F. MACRO MARKS (Overlay)
    for i in range(9):
        if game.macro_board[i] != 0:
            r, c = i // 3, i % 3
            center = (c*GRID_SIZE + GRID_SIZE//2, r*GRID_SIZE + GRID_SIZE//2)
            txt = "X" if game.macro_board[i] == 1 else "O"
            col = COLOR_X if game.macro_board[i] == 1 else COLOR_O
            
            t_surf = font_big.render(txt, True, col)
            t_surf.set_alpha(60) # Transparent
            t_rect = t_surf.get_rect(center=center)
            surface.blit(t_surf, t_rect)

    # Output
    raw = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", (GAME_RES, GAME_RES), raw)

# --- 6. LOGIC ---
def process_click(x, y):
    game = st.session_state.game
    if game.game_over: return

    # Map click to index
    # Note: If the image is displayed at a different width in browser, 
    # Streamlit coordinates might need scaling. 
    # But usually streamlit-image-coordinates returns relative to image pixel size if width matches.
    
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    
    # Validation logic
    major_col, minor_col = col // 3, col % 3
    major_row, minor_row = row // 3, row % 3
    grid_idx = major_row * 3 + major_col
    cell_idx = minor_row * 3 + minor_col
    action = (grid_idx * 9) + cell_idx

    if action in game.get_valid_moves():
        game.make_move(action)
        st.session_state.last_move = action
        
        # Check Win
        check_win()
        
        # AI Turn
        if not game.game_over:
            with st.spinner("SYSTEM PROCESSING..."):
                move = st.session_state.ai.search(game)
                game.make_move(move)
                st.session_state.last_move = move
                check_win()
        st.rerun()

def check_win():
    game = st.session_state.game
    if game.game_over:
        st.session_state.game_over = True
        if game.winner == 1:
            st.session_state.wins_user += 1
        elif game.winner == -1:
            st.session_state.wins_ai += 1

# --- 7. MAIN LAYOUT ---

st.title("ULTIMATE // TIC-TAC-TOE")

# Create a container to center things vertically if needed
main_cols = st.columns([1.5, 2, 1.5]) # Left Spacer, Game, Right Stats

# We use a Layout: [Board (Left)] --- [Stats (Right)]
layout_cols = st.columns([1, 0.1, 0.6]) # 1 unit Board, gap, 0.6 unit Stats

with layout_cols[0]:
    # RENDER BOARD
    img = render_game_image(st.session_state.game, st.session_state.last_move)
    # We display it using coordinates component
    # We leave width=None so it uses the natural image size (600px) which fits nicely
    click = streamlit_image_coordinates(img, key="main_board")
    
    if click is not None:
        process_click(click['x'], click['y'])

with layout_cols[2]:
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    
    # STATUS INDICATOR
    status_text = "READY"
    status_color = "#888"
    
    game = st.session_state.game
    if game.game_over:
        if game.winner == 1: 
            status_text = "VICTORY"
            status_color = "#00ff00"
        elif game.winner == -1: 
            status_text = "DEFEAT"
            status_color = "#ff0000"
        else: 
            status_text = "DRAW"
            status_color = "orange"
    elif game.current_player == -1:
        status_text = "AI THINKING..."
        status_color = "#00f3ff"
    else:
        status_text = "YOUR TURN"
        status_color = "#fff"

    st.markdown(f"""
    <div style="text-align: center; border: 2px solid {status_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="margin:0; color: {status_color};">{status_text}</h3>
    </div>
    """, unsafe_allow_html=True)

    # SCOREBOARD
    score_cols = st.columns(2)
    with score_cols[0]:
        st.markdown(f"""
        <div class="score-box">
            <div class="score-val" style="color: #ff2e50;">{st.session_state.wins_user}</div>
            <div class="score-label">PLAYER</div>
        </div>
        """, unsafe_allow_html=True)
    with score_cols[1]:
        st.markdown(f"""
        <div class="score-box">
            <div class="score-val" style="color: #00f3ff;">{st.session_state.wins_ai}</div>
            <div class="score-label">AI AGENT</div>
        </div>
        """, unsafe_allow_html=True)

    # CONTROLS
    st.markdown("---")
    if st.button("INITIATE NEW GAME"):
        st.session_state.game = UltimateTicTacToe()
        st.session_state.game_over = False
        st.session_state.last_move = None
        st.rerun()

    if st.button("RESET SYSTEM SCORES"):
        st.session_state.wins_user = 0
        st.session_state.wins_ai = 0
        st.rerun()

    # LEGEND
    st.markdown("""
    <div style="margin-top: 20px; font-size: 0.8rem; color: #666;">
    <b>LEGEND:</b><br>
    <span style="color:#00f3ff">■</span> Macro Grid<br>
    <span style="color:#203050">■</span> Valid Zone<br>
    <span style="color:#ffb400">■</span> Last Move
    </div>
    """, unsafe_allow_html=True)