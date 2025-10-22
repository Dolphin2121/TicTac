import pygame
import sys
import traceback

#Constants 
WINDOW_SIZE = 450  # window is square
BOARD_SIZE = 3     # 3x3 Tic-Tac-Toe
LINE_THICKNESS = 6
BOARD_COLOR = (30, 30, 40)
LINE_COLOR = (200, 200, 210)
X_COLOR = (220, 50, 50)
O_COLOR = (60, 180, 200)
TEXT_COLOR = (230, 230, 230)

SQUARE = WINDOW_SIZE // BOARD_SIZE
MARK_PADDING = 20  # padding inside a square for drawing X
FONT_SIZE_UI = 20
FONT_SIZE_END = 36

SCORE_FILE = "ttt_scores.txt"  # scoreboard save file



def safe_init_pygame():
    #Initialize pygame and return display surface and fonts. Raise on fatal failure.
    try:
        pygame.init()
        pygame.mixer.init()

        screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 80))
        pygame.display.set_caption("Custom Tic-Tac-Toe")
        ui_font = pygame.font.SysFont(None, FONT_SIZE_UI)
        end_font = pygame.font.SysFont(None, FONT_SIZE_END)

        win_sound = pygame.mixer.Sound("mixkit-retro-game-notification-212.wav")
        click_sound = pygame.mixer.Sound("Perc_MusicStand_lo.wav")
        click_sound.set_volume(1.0)
        return screen, ui_font, end_font, click_sound, win_sound
    except Exception as e:
        # If Pygame can't initialize, raise a helpful error.
        raise RuntimeError("Pygame failed to initialize: " + str(e))

def create_empty_board():
    #Return a 3x3 board filled with None for empty cells.
    return [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def draw_board_lines(surface):
    #Draw the grid lines on the board area.
    for i in range(1, BOARD_SIZE):
        # Horizontal lines
        pygame.draw.line(surface, LINE_COLOR, (0, i * SQUARE), (WINDOW_SIZE, i * SQUARE), LINE_THICKNESS)
        # Vertical lines
        pygame.draw.line(surface, LINE_COLOR, (i * SQUARE, 0), (i * SQUARE, WINDOW_SIZE), LINE_THICKNESS)

def draw_marks(surface, board):
    #Draw X and O marks in their board squares.
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            mark = board[row][col]
            center_x = col * SQUARE + SQUARE // 2
            center_y = row * SQUARE + SQUARE // 2
            if mark == "X":
                # draw X as two thick lines
                start1 = (col * SQUARE + MARK_PADDING, row * SQUARE + MARK_PADDING)
                end1   = (col * SQUARE + SQUARE - MARK_PADDING, row * SQUARE + SQUARE - MARK_PADDING)
                start2 = (col * SQUARE + MARK_PADDING, row * SQUARE + SQUARE - MARK_PADDING)
                end2   = (col * SQUARE + SQUARE - MARK_PADDING, row * SQUARE + MARK_PADDING)
                pygame.draw.line(surface, X_COLOR, start1, end1, LINE_THICKNESS)
                pygame.draw.line(surface, X_COLOR, start2, end2, LINE_THICKNESS)
            elif mark == "O":
                radius = SQUARE // 2 - MARK_PADDING
                pygame.draw.circle(surface, O_COLOR, (center_x, center_y), radius, LINE_THICKNESS)

def get_cell_from_position(pos):
    #Convert mouse position to board (row, col). Returns (row, col) or None if out of board.
    x, y = pos
    if x < 0 or x >= WINDOW_SIZE or y < 0 or y >= WINDOW_SIZE:
        return None
    return (y // SQUARE, x // SQUARE)

def check_winner(board):
    #Check board for a winner.
    #Returns "X" or "O" if someone won, "TIE" if full with no winner, or None otherwise.
    # Check rows and columns
    for i in range(BOARD_SIZE):
        # Row check
        if board[i][0] is not None and all(board[i][j] == board[i][0] for j in range(BOARD_SIZE)):
            return board[i][0]
        # Column check
        if board[0][i] is not None and all(board[j][i] == board[0][i] for j in range(BOARD_SIZE)):
            return board[0][i]

    # Diagonals
    if board[0][0] is not None and all(board[i][i] == board[0][0] for i in range(BOARD_SIZE)):
        return board[0][0]
    if board[0][BOARD_SIZE-1] is not None and all(board[i][BOARD_SIZE-1-i] == board[0][BOARD_SIZE-1] for i in range(BOARD_SIZE)):
        return board[0][BOARD_SIZE-1]

    # Check for tie (full board)
    if all(board[r][c] is not None for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
        return "TIE"

    return None

def draw_ui(surface, ui_font, scores, current_player, game_over, winner_text):
    #Draw the scoreboard, instructions, and status on the bottom UI area.
    # Clear bottom UI area
    ui_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE, 80)
    pygame.draw.rect(surface, BOARD_COLOR, ui_rect)

    # Scoreboard text
    score_text = f"X: {scores['X']}   O: {scores['O']}   Ties: {scores['TIES']}"
    score_surface = ui_font.render(score_text, True, TEXT_COLOR)
    surface.blit(score_surface, (10, WINDOW_SIZE + 8))

    # Current player or result text
    if game_over:
        result_surface = ui_font.render(winner_text + "   (Press R to replay round, N for new match)", True, TEXT_COLOR)
    else:
        result_surface = ui_font.render(f"Turn: {current_player}   (Click board to play)   R: reset round  N: new match", True, TEXT_COLOR)
    surface.blit(result_surface, (10, WINDOW_SIZE + 36))

def save_scores_to_file(scores):
    #Attempt to save scores to a text file. Errors are caught by caller.
    with open(SCORE_FILE, "w") as f:
        f.write(f"X:{scores['X']}\n")
        f.write(f"O:{scores['O']}\n")
        f.write(f"TIES:{scores['TIES']}\n")

def load_scores_from_file():
    #Load scores from file if present. Returns default scores on error.
    default = {"X": 0, "O": 0, "TIES": 0}
    try:
        with open(SCORE_FILE, "r") as f:
            lines = f.read().splitlines()
        result = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().upper()
                val = val.strip()
                result[key] = int(val)
        # Validate and return
        return {"X": result.get("X", 0), "O": result.get("O", 0), "TIES": result.get("TIES", 0)}
    except Exception:
        # If anything goes wrong, return defaults (we handle errors gracefully)
        return default

# Main Program

def main():
    # Initialize pygame safely
    try:
        screen, ui_font, end_font, click_sound, win_sound = safe_init_pygame()
    except RuntimeError as init_error:
        print("Fatal error: ", init_error)
        sys.exit(1)

    # Game state variables
    board = create_empty_board()
    current_player = "X"
    scores = load_scores_from_file()  # best-effort load
    game_over = False
    winner_text = ""
    clock = pygame.time.Clock()

    # Draw initial board
    screen.fill(BOARD_COLOR)
    draw_board_lines(screen)
    draw_marks(screen, board)
    pygame.display.update()

    # Main loop
    running = True
    while running:

        for event in pygame.event.get():
            # Quit handling
            if event.type == pygame.QUIT:
                running = False

            # Mouse click: place mark if allowed
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                try:
                    cell = get_cell_from_position(event.pos)
                    if cell is None:
                        # click outside board area (e.g., UI area) -> ignore
                        continue
                    row, col = cell
                    # Defensive checks: valid indices
                    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                        continue
                    if board[row][col] is None:
                        click_sound.play() #plays sound for everytime you click 
                        board[row][col] = current_player
                        # Check for a game result
                        result = check_winner(board)
                        if result == "X" or result == "O":
                            win_sound.play() #plays sound for the winner 
                            scores[result] += 1
                            winner_text = f"{result} wins!"
                            game_over = True
                            # Try to save scores; handle file errors gracefully
                            try:
                                save_scores_to_file(scores)
                            except Exception as file_err:
                                print("Warning: could not save scores:", file_err)
                        elif result == "TIE":
                            scores["TIES"] += 1
                            winner_text = "Tie!"
                            game_over = True
                            try:
                                save_scores_to_file(scores)
                            except Exception as file_err:
                                print("Warning: could not save scores:", file_err)
                        else:
                            # Switch turns if no result
                            current_player = "O" if current_player == "X" else "X"
                    else:
                        # clicked an occupied cell -> ignore or beep? We'll just ignore but could add feedback.
                        pass
                except Exception as e:
                    # Catch unexpected errors in click handling, continue running
                    print("Error processing click:", e)
                    traceback.print_exc()

            # Keyboard handling (reset round, new match)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset only the board for a new round (keep scores)
                    board = create_empty_board()
                    current_player = "X"
                    game_over = False
                    winner_text = ""
                elif event.key == pygame.K_n:
                    # Reset scoreboard and board (new match)
                    board = create_empty_board()
                    current_player = "X"
                    scores = {"X": 0, "O": 0, "TIES": 0}
                    game_over = False
                    winner_text = ""
                    # Try to remove or reset the score file
                    try:
                        save_scores_to_file(scores)
                    except Exception as e:
                        print("Warning: failed to reset score file:", e)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Draw everything each frame
        try:
            screen.fill(BOARD_COLOR)
            draw_board_lines(screen)
            draw_marks(screen, board)
            draw_ui(screen, ui_font, scores, current_player, game_over, winner_text)
            if game_over:
                # Big centered text to show the winner/tie
                center_message = end_font.render(winner_text, True, TEXT_COLOR)
                msg_rect = center_message.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
                screen.blit(center_message, msg_rect)
            pygame.display.flip()
        except Exception as render_err:
            print("Render error:", render_err)
            traceback.print_exc()
            # On rendering errors, break loop to avoid infinite noisy failure
            running = False

    # Clean up pyame on exit
    pygame.quit()

# Entry point guard
if __name__ == "__main__":
    try:
        main()
    except Exception as fatal:
        # Catch-all guard so the program never crashes silently
        print("A fatal error occurred. See traceback below.")
        traceback.print_exc()
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)

