"""
Модуль для логики игры в шашки
"""

import time
from typing import List, Tuple, Optional, Set
from .constants import BOARD_SIZE, INITIAL_TIME_SECONDS
from .enums import PieceType, Player
from .models import Piece

class CheckersGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = Player.WHITE
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.white_time = INITIAL_TIME_SECONDS
        self.black_time = INITIAL_TIME_SECONDS
        self.last_time_update = time.time()
        self.multiple_capture = False
        self.captured_pieces_to_highlight = []
        self.setup_board()
        self.move_history = []

    def setup_board(self):
        # Расставляем черные шашки (сверху)
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(Player.BLACK)

        # Расставляем белые шашки (снизу)
        for row in range(5, BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(Player.WHITE)

    def update_timer(self):
        current_time = time.time()
        time_passed = current_time - self.last_time_update

        if not self.game_over:
            if self.current_player == Player.WHITE:
                self.white_time -= time_passed
                if self.white_time <= 0:
                    self.white_time = 0
                    self.game_over = True
                    self.winner = Player.BLACK
            else:
                self.black_time -= time_passed
                if self.black_time <= 0:
                    self.black_time = 0
                    self.game_over = True
                    self.winner = Player.WHITE

        self.last_time_update = current_time

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_piece(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

