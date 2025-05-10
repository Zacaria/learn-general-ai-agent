import chess
from smolagents import Tool, CodeAgent
from src.models import general_model

class ChessBestMoveTool(Tool):
    name = "ChessBestMoveTool"
    description = (
        "Given a FEN string and the current player, returns the best next move in algebraic notation."
    )
    inputs = {
        "fen": {
            "description": "FEN string representing the board state",
            "type": "string"
        },
        "player": {
            "description": "'white' or 'black'. If not provided, inferred from FEN.",
            "type": "string",
            "optional": True,
            "nullable": True
        }
    }
    output_type = "string"
    
    def forward(self, fen: str, player: str = None) -> str:
        """
        Args:
            fen (str): FEN string representing the board state
            player (str, optional): 'white' or 'black'. If not provided, inferred from FEN.
        Returns:
            str: Best move in algebraic notation (UCI or SAN)
        """
        board = chess.Board(fen)
        # Optionally flip the board if player is specified and doesn't match turn
        if player:
            if (player.lower() == 'white' and not board.turn) or (player.lower() == 'black' and board.turn):
                board.turn = not board.turn
        # Try to get the best move (simple: highest material gain, fallback: first legal move)
        best_move = None
        best_score = -float('inf') if board.turn else float('inf')
        for move in board.legal_moves:
            board.push(move)
            score = sum([piece.piece_type for piece in board.piece_map().values() if piece.color == board.turn])
            board.pop()
            if board.turn:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
        if not best_move:
            best_move = next(iter(board.legal_moves), None)
        if not best_move:
            return "No legal moves available."
        return board.san(best_move)

class ChessWinningMove(Tool):
    name = "ChessWinningMove"
    description = (
        "Given a FEN string and the current player, returns the winning move in algebraic notation."
    )
    inputs = {
        "fen": {
            "description": "FEN string representing the board state",
            "type": "string"
        },
        "player": {
            "description": "'white' or 'black'",
            "type": "string",
        }
    }
    output_type = "string"
    
    def forward(self, fen: str, player: str) -> str:
        board = chess.Board(fen)
        if player.lower() == 'white' and not board.turn:
            board.turn = not board.turn
        elif player.lower() == 'black' and board.turn:
            board.turn = not board.turn
        return board.san(next(iter(board.legal_moves)))

system_prompt = (
    f"You are a specialized agent in chess problem solving."
    f"You must help answering the user's question by the next winning move in algebraic notation for the current board state."
    f"You should only base your answer on the information gathered from the chess board and relevent to the question"
    f"You should rely on your ChessWinningMove tool to find the next winning move"
    f"Before answering, you must control that the answer corresponds to the requested move, by running a few times to check the result"
    # f"If the answer is not the best move, try to find the best move."
    f"If the answer cannot be found or inferred from the chess board, respond with: 'EXCEPTION: The chess board does not allow answering the question.'"
)

chess_agent = CodeAgent(
    model=general_model,
    tools=[ChessWinningMove()],
    add_base_tools=True,
    # max_steps=10,
    name="ChessAgent",
    planning_interval=3,
    additional_authorized_imports=["chess"],
    description="This agent is responsible for helping with chess problem solving."
)

chess_agent.memory.system_prompt.system_prompt += f"\n{system_prompt}"