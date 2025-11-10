import customtkinter as ctk
from tkinter import messagebox
import math, time, threading, random
from playsound import playsound
import os

# --- Game Logic ---
def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != '':
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2]
    return None

def is_moves_left(board):
    return any('' in row for row in board)

def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == 'O':
        return 10 - depth
    elif winner == 'X':
        return depth - 10
    elif not is_moves_left(board):
        return 0

    if is_maximizing:
        best = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == '':
                    board[i][j] = 'O'
                    val = minimax(board, depth + 1, False, alpha, beta)
                    board[i][j] = ''
                    best = max(best, val)
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == '':
                    board[i][j] = 'X'
                    val = minimax(board, depth + 1, True, alpha, beta)
                    board[i][j] = ''
                    best = min(best, val)
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
        return best

def find_best_move(board):
    best_val = -math.inf
    best_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                board[i][j] = 'O'
                move_val = minimax(board, 0, False, -math.inf, math.inf)
                board[i][j] = ''
                if move_val > best_val:
                    best_val = move_val
                    best_move = (i, j)
    return best_move

# --- CustomTkinter GUI ---
class TicTacToeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("🎮 Modern Tic-Tac-Toe (AI)")
        self.geometry("420x540")
        self.resizable(False, False)

        self.player_name = ctk.StringVar(value="Player")
        self.scores = {"Player": 0, "AI": 0, "Draw": 0}

        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        self.create_intro()

    # --- Intro Screen ---
    def create_intro(self):
        for widget in self.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self, fg_color=("gray14", "gray20"), corner_radius=15)
        frame.pack(pady=80, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Welcome to Tic-Tac-Toe", text_color="#00ADB5",
                     font=("Helvetica", 22, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text="Enter your name:", text_color="white", font=("Arial", 14)).pack(pady=5)
        ctk.CTkEntry(frame, textvariable=self.player_name, placeholder_text="Your name",
                     font=("Arial", 14), width=220).pack(pady=10)
        ctk.CTkButton(frame, text="Start Game", command=self.start_game,
                      fg_color="#00ADB5", hover_color="#007C89",
                      font=("Arial", 16, "bold"), corner_radius=10).pack(pady=20)

    # --- Game Screen ---
    def start_game(self):
        for widget in self.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self, text=f"{self.player_name.get()} (X) vs AI (O)",
                             font=("Helvetica", 18, "bold"), text_color="#FFD369")
        title.pack(pady=15)

        frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("gray14", "gray20"))
        frame.pack(pady=10)

        for i in range(3):
            for j in range(3):
                btn = ctk.CTkButton(frame, text="", width=100, height=100,
                                    fg_color="#393E46", hover_color="#00ADB5",
                                    font=("Helvetica", 40, "bold"),
                                    corner_radius=20,
                                    command=lambda r=i, c=j: self.player_move(r, c))
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.buttons[i][j] = btn

        self.status = ctk.CTkLabel(self, text=f"{self.player_name.get()}'s turn (X)",
                                   font=("Arial", 14), text_color="#EEEEEE")
        self.status.pack(pady=10)

        self.score_label = ctk.CTkLabel(self, text=self.get_score_text(),
                                        font=("Arial", 13), text_color="#00ADB5")
        self.score_label.pack(pady=5)

        bottom = ctk.CTkFrame(self, fg_color="#222831")
        bottom.pack(pady=15)
        ctk.CTkButton(bottom, text="🔁 Play Again", width=120, command=self.reset_board,
                      fg_color="#00ADB5", hover_color="#007C89", corner_radius=10).grid(row=0, column=0, padx=5)
        ctk.CTkButton(bottom, text="❌ Exit", width=120, command=self.destroy,
                      fg_color="#FF5722", hover_color="#E64A19", corner_radius=10).grid(row=0, column=1, padx=5)

    # --- Logic ---
    def player_move(self, r, c):
        if self.board[r][c] == '' and check_winner(self.board) is None:
            self.board[r][c] = 'X'
            self.buttons[r][c].configure(text='X', text_color="#00ADB5")
            self.play_sound("click.wav")
            self.animate_button(self.buttons[r][c])

            winner = check_winner(self.board)
            if winner:
                self.end_game(winner)
                return
            elif not is_moves_left(self.board):
                self.end_game(None)
                return

            self.status.configure(text="AI is thinking...")
            threading.Thread(target=self.ai_move).start()

    def ai_move(self):
        time.sleep(random.uniform(0.6, 1.2))
        move = find_best_move(self.board)
        if move != (-1, -1):
            self.board[move[0]][move[1]] = 'O'
            self.buttons[move[0]][move[1]].configure(text='O', text_color="#FF5722")
            self.play_sound("move.wav")
            self.animate_button(self.buttons[move[0]][move[1]])

        winner = check_winner(self.board)
        if winner:
            self.end_game(winner)
        elif not is_moves_left(self.board):
            self.end_game(None)
        else:
            self.status.configure(text=f"{self.player_name.get()}'s turn (X)")

    def end_game(self, winner):
        if winner == 'X':
            msg = f"🎉 {self.player_name.get()} wins!"
            self.scores["Player"] += 1
            self.play_sound("win.wav")
        elif winner == 'O':
            msg = "💻 AI wins!"
            self.scores["AI"] += 1
            self.play_sound("lose.wav")
        else:
            msg = "🤝 It's a draw!"
            self.scores["Draw"] += 1
            self.play_sound("draw.wav")

        self.status.configure(text=msg)
        self.score_label.configure(text=self.get_score_text())
        messagebox.showinfo("Game Over", msg)

    def reset_board(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].configure(text='', fg_color="#393E46")
        self.status.configure(text=f"{self.player_name.get()}'s turn (X)")

    def get_score_text(self):
        return f"🏆 {self.player_name.get()}: {self.scores['Player']}  |  💻 AI: {self.scores['AI']}  |  🤝 Draws: {self.scores['Draw']}"

    def animate_button(self, button):
        """Subtle pulse animation on move"""
        def pulse():
            original = button.cget("fg_color")
            for color in ["#00ADB5", "#007C89"] if button.cget("text") == "X" else ["#FF5722", "#E64A19"]:
                button.configure(fg_color=color)
                time.sleep(0.1)
            button.configure(fg_color=original)
        threading.Thread(target=pulse).start()

    def play_sound(self, sound):
        threading.Thread(target=lambda: playsound(sound, block=False)).start()


# --- Run the Game ---
if __name__ == "__main__":
    # Create dummy sound files if not present
    for s in ["click.wav", "move.wav", "win.wav", "lose.wav", "draw.wav"]:
        if not os.path.exists(s):
            open(s, "wb").close()

    app = TicTacToeApp()
    app.mainloop()
