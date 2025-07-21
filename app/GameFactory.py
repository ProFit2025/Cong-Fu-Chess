import pathlib
from app.Board import Board
from app.Game import Game
from app.Img import Img
from app.PieceFactory import PieceFactory
import pandas as pd

class GameFactory:
    def create(self) -> Game:
        board = self.load_board('my_board.png')
        game_pieces = []
    
        board_pieces = pd.read_csv('board.csv')
        piece_factory = PieceFactory(board, 'pieces')
        for i in range(board_pieces.shape[0]):
            for j in range(board_pieces.shape[1]):
                p_type = board_pieces.iloc[i][j]
                if pd.isna(p_type) or not isinstance(p_type, str):
                    continue
                
                p = piece_factory.create_piece(p_type, (i, j))
                game_pieces.append(p)
        
        game = Game(game_pieces, board)
        return game    
        
    def load_board(self, board_path: pathlib.Path) -> Board:
        board_img = Img().read(board_path, [800, 800])
        board = Board(100, 100, 0.2, 0.2, 8, 8, board_img)
        return board
