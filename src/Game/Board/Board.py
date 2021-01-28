from .Square import Square
from .Piece import Piece
from .Position import Position
from .BoardErrors import InvalidPositionError, NoPieceError, EmptySquareError, InvalidMoveError, InvalidPieceCheckError, InvalidCastleError
from ..Utils import get_opponent_color, get_direction, get_castle_rank, get_pawn_rank, get_color_prefix
import copy
from numpy import ndarray

class Board:
	def __init__(self):
		self.board = ndarray((8,8),dtype=object)
		self.turns_since_last_capture = 0
		self.board_encodings = []
		self.pieces = {
			"white":
			{
				"pawns": 8,
				"rooks": 2,
				"knights": 2,
				"bishops": 2,
				"queens": 1
			},
			"black":
			{
				"pawns": 8,
				"rooks": 2,
				"knights": 2,
				"bishops": 2,
				"queens": 1
			},
		}
		self.king_positions = {
			"white": Position(0,4),
			"black": Position(7,4)
		}
		for file in range(8):
			self.board[1,file] = Square(Position(1,file),Piece("pawn","white","wp" + str(file) + "1"))
			self.board[6,file] = Square(Position(6,file),Piece("pawn","black","wp" + str(file) + "6"))

		self.board[0,0] = Square(Position(0,0),Piece("rook","white","wRa1"))
		self.board[0,7] = Square(Position(0,7),Piece("rook","white","wRh1"))
		self.board[7,0] = Square(Position(7,0),Piece("rook","black","bRa8"))
		self.board[7,7] = Square(Position(7,7),Piece("rook","black","bRh8"))

		self.board[0,1] = Square(Position(0,1),Piece("knight","white","wNb1"))
		self.board[0,6] = Square(Position(0,6),Piece("knight","white","wNg1"))
		self.board[7,1] = Square(Position(7,1),Piece("knight","black","bNb8"))
		self.board[7,6] = Square(Position(7,6),Piece("knight","black","bNg8"))

		self.board[0,2] = Square(Position(0,2),Piece("bishop","white","wBc1"))
		self.board[0,5] = Square(Position(0,5),Piece("bishop","white","wBf1"))
		self.board[7,2] = Square(Position(7,2),Piece("bishop","black","bBc8"))
		self.board[7,5] = Square(Position(7,5),Piece("bishop","black","bBf8"))

		self.board[0,3] = Square(Position(0,3),Piece("queen","white","wQd1"))
		self.board[0,4] = Square(Position(0,4),Piece("king","white","wKe1"))
		self.board[7,3] = Square(Position(7,3),Piece("queen","black","bQd8"))
		self.board[7,4] = Square(Position(7,4),Piece("king","black","bKe8"))

		for file in range(8):
			for rank in range(4):
				self.board[rank+2,file] = Square(Position(rank+2,file),Piece("nopiece","none","np"))

		self.evaluate_attacked_squares()
		self.evaluate_valid_moves()

	def highlight_possible_moves(self,position):
		if self.is_valid_position(position):
			piece = self.board[position.rank,position.file].piece
			if piece.type != "nopiece":
				self.board[position.rank,position.file].is_highlighted = True
				for rank in range(8):
					for file in range(8):
						if self.is_valid_move(piece,position,Position(rank,file)):
							self.board[rank,file].is_highlighted = True
			else:
				raise EmptySquareError(position,piece.color)
		else:
			raise InvalidPositionError(position)

	def make_move(self,start,end,turn_color,promotion_type):
		if start != end:
			if self.is_valid_position(start):
				if self.is_valid_position(end):
					piece_to_move = self.board[start.rank,start.file].piece
					piece_to_take = self.board[end.rank,end.file].piece
					if piece_to_move.type != "nopiece":
						if self.is_valid_move(piece_to_move,start,end):
							self.move_piece(start,end,turn_color,promotion_type,piece_to_move,piece_to_take)
							self.unhighlight_squares()
							self.evaluate_attacked_squares()
							self.clear_en_pessantability(turn_color)
						else:
							raise InvalidMoveError(piece_to_move.type,start,end)
					else:
						raise NoPieceError(start,turn_color)
				else:
					raise InvalidPositionError(end)
			else:
				raise InvalidPositionError(end)
		else:
			raise SameSquareError(start)

	def move_piece(self,start,end,turn_color,promotion_type,piece_to_move,piece_to_take):
		opponent_color = get_opponent_color(turn_color)
		if self.is_check(opponent_color) and piece_to_move.type != "king":
			raise InvalidPieceCheckError(piece_to_move.type)

		if piece_to_move.type == "pawn" :
			if end.rank == 0 or end.rank == 7:
				if promotion_type == "queen":
					piece_to_move.type = "queen"
				elif promotion_type == "rook":
					piece_to_move.type = "rook"
				elif promotion_type == "knight":
					piece_to_move.type = "knight"
				elif promotion_type == "bishop":
					piece_to_move.type = "bishop"
				else:
					raise InvalidPromotionTypeError(start,end)
				self.pieces[turn_color][promotion_type] += 1
				self.pieces[turn_color]["pawn"] -= 1
			elif abs(end.file-start.file) == 2:
				direction = get_direction(turn_color)
				self.board[start.rank+direction*1,start.file].is_en_pessantable_by[opponent_color] = True

		if piece_to_take.type != "nopiece":
			self.take_piece(piece_to_take,turn_color)
		else:
			self.turns_since_last_capture += 1

		if piece_to_move.type == "king":
			self.king_positions[turn_color] = copy.deepcopy(end)

		piece_to_move.position = copy.deepcopy(end)
		piece_to_move.has_moved = True
		self.board[end.rank,end.file].piece = copy.deepcopy(piece_to_move)
		self.board[start.rank,start.file].piece = Piece("nopiece","none","np")

	def castle(self,turn_color,direction):
		castle_rank = get_castle_rank(turn_color)
		opponent_color = get_opponent_color(turn_color)

		king_position = self.king_positions[turn_color]
		if king_position == Position(castle_rank,4) and not self.board[king_position.rank,king_position.file].piece.has_moved and not self.is_check(opponent_color):
			if direction == "short":
				corner_piece = self.board[castle_rank,7].piece
				inner_square_1 = self.board[castle_rank,5]
				inner_square_2 = self.board[castle_rank,6]
				if corner_piece.type == "rook" and not corner_piece.has_moved and inner_square_1.piece.type == "nopiece" and not inner_square_1.is_attacked_by[opponent_color] and inner_square_2.piece.type == "nopiece" and not inner_square_2.is_attacked_by[opponent_color]:
					king = self.board[castle_rank,4].piece
					king.has_moved = True
					self.board[castle_rank,6].piece = copy.deepcopy(king)

					corner_piece.has_moved = True
					self.board[castle_rank,5].piece = copy.deepcopy(corner_piece)

					self.board[castle_rank,4].piece = Piece("nopiece","none","np")
					self.board[castle_rank,7].piece = Piece("nopiece","none","np")
				else:
					raise InvalidCastleError(turn_color)
			elif direction == "long":
				corner_piece = self.board[castle_rank,0].piece
				inner_square_1 = self.board[castle_rank,1]
				inner_square_2 = self.board[castle_rank,2]
				inner_square_3 = self.board[castle_rank,3]
				if corner_piece.type == "rook" and not corner_piece.has_moved and inner_square_1.piece.type == "nopiece"  and not inner_square_1.is_attacked_by[opponent_color] and inner_square_2.piece.type == "nopiece" and not inner_square_2.is_attacked_by[opponent_color] and inner_square_3.piece.type == "nopiece" and not inner_square_3.is_attacked_by[opponent_color]:
					king = self.board[castle_rank,4].piece
					king.has_moved = True
					self.board[castle_rank,2].piece = copy.deepcopy(king)

					corner_piece.has_moved = True
					self.board[castle_rank,3].piece = copy.deepcopy(corner_piece)

					self.board[castle_rank,4].piece = Piece("nopiece","none","np")
					self.board[castle_rank,0].piece = Piece("nopiece","none","np")
				else:
					raise InvalidCastleError(turn_color)
			else:
				raise InvalidCastleError(turn_color)

			self.unhighlight_squares()
			self.evaluate_attacked_squares()
			self.clear_en_pessantability(turn_color)
		else:
			raise InvalidCastleError(turn_color)

	def is_valid_position(self,position):
		rank = position.rank
		file = position.file
		if rank >= 0 and rank <= 7 and file >= 0 and file <= 7:
			return True
		else:
			return False

	def is_valid_move(self,piece,start,end):
		if piece.type == "pawn":
			return self.is_valid_move_pawn(start,end,piece)
		elif piece.type == "rook":
			return self.is_valid_move_rook(start,end,piece)
		elif piece.type == "knight":
			return self.is_valid_move_knight(start,end,piece)
		elif piece.type == "bishop":
			return self.is_valid_move_bishop(start,end,piece)
		elif piece.type == "queen":
			return self.is_valid_move_queen(start,end,piece)
		elif piece.type == "king":
			return self.is_valid_move_king(start,end,piece)
		else:
			raise NoPieceError(start,piece.color)

	def is_valid_move_pawn(self,start,end,piece):
		direction = get_direction(piece.color)
		opponent_color = get_opponent_color(piece.color)

		temp_position = Position(0,0)

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file
		if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.type == "nopiece" and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*2
		temp_position.file = start.file
		if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.type == "nopiece" and self.board[start.rank+direction*1,start.file].piece.type == "nopiece" and not piece.has_moved and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file-1
		if self.is_valid_position(temp_position) and piece.id in self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color] and self.board[temp_position.rank,temp_position.file].piece.color == opponent_color and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file+1
		if self.is_valid_position(temp_position) and piece.id in self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color] and self.board[temp_position.rank,temp_position.file].piece.color == opponent_color and end == temp_position:
			return True	

		return False

	def is_valid_move_rook(self,start,end,piece):
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color]

	def is_valid_move_knight(self,start,end,piece):
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color]

	def is_valid_move_bishop(self,start,end,piece):
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color]

	def is_valid_move_queen(self,start,end,piece):
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color]

	def is_valid_move_king(self,start,end,piece):
		opponent_color = get_opponent_color(piece.color)
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color] and not self.board[end.rank,end.file].is_attacked_by[opponent_color]

	def take_piece(self,piece_to_take,piece_color):
		if piece_to_take.type == "pawn":
			self.pieces[piece_color]["pawns"] -= 1
		elif piece_to_take.type == "rook":
			self.pieces[piece_color]["rooks"] -= 1
		elif piece_to_take.type == "knight":
			self.pieces[piece_color]["knights"] -= 1
		elif piece_to_take.type == "bishop":
			self.pieces[piece_color]["bishops"] -= 1
		elif piece_to_take.type == "queen":
			self.pieces[piece_color]["queens"] -= 1
		self.turns_since_last_capture = 0

	def is_checkmate(self,turn_color):
		if self.is_check(turn_color):
			king_color = "white"
			if turn_color == "white":
				king_color = "black"
			king_position = self.king_positions[king_color]
			king = self.board[king_position.rank,king_position.file]
			position_shifts = [-1,0,1]
			checkmate = True

			temp_position = Position(0,0)

			for rank_shift in position_shifts:
				for file_shift in position_shifts:
					temp_position.rank = king_position.rank+rank_shift
					temp_position.file = king_position.file+file_shift
					if king.id in self.board[rank,file].valid_moves:
						checkmate = False
						break
			return checkmate
		else:
			return False

	def is_check(self,turn_color):
		king_color = get_opponent_color(turn_color)
		king_position = self.king_positions[king_color]
		return self.board[king_position.rank,king_position.file].is_attacked_by[turn_color]

	def is_draw(self,turn_color):
		return self.is_fifty_move_no_cap() or self.is_stalemate(turn_color) or self.is_three_move_repetition()

	def is_fifty_move_no_cap(self):
		return self.turns_since_last_capture >= 100

	def is_stalemate(self,turn_color):
		any_valid_moves = False
		color_prefix = get_color_prefix(turn_color)
		for rank in range(8):
			for file in range(8):
				if color_prefix in self.board[rank,file].valid_moves_color:
					any_valid_moves = True
		return not any_valid_moves and not self.is_check(get_opponent_color(turn_color))

	def is_three_move_repetition(self):
		return len(self.board_encodings) == 6 and self.board_encodings[0] == self.board_encodings[2] and self.board_encodings[0] == self.board_encodings[4] and self.board_encodings[1] == self.board_encodings[3] and self.board_encodings[1] == 5

	def evaluate_valid_moves(self):
		temp_position = Position(0,0)
		temp_position2 = Position(0,0)
		for rank in range(8):
			for file in range(8):
				self.board[rank,file].valid_moves = self.board[rank,file].is_attacked_by["white"] + self.board[rank,file].is_attacked_by["black"]
				self.board[rank,file].valid_moves_color = []
				if self.board[rank,file].is_attacked_by["white"] and not "w" in self.board[rank,file].valid_moves_color:
					self.board[rank,file].valid_moves_color.append("w")
				if self.board[rank,file].is_attacked_by["black"] and not "b" in self.board[rank,file].valid_moves_color:
					self.board[rank,file].valid_moves_color.append("b")

		for rank in range(8):
			temp_position.rank = rank 
			temp_position2.rank = rank
			for file in range(8):
				piece = self.board[rank,file].piece 
				temp_position.file = file

				if piece.type == "pawn":
					temp_position2.file = file + get_direction(piece.color)*1
					if self.is_valid_move_pawn(temp_position,temp_position2,piece):
						self.board[temp_position2.rank,temp_position2.file].valid_moves.append(piece.id)

					if rank == 1 or rank == 6:
						temp_position2.file = file + get_direction(piece.color)*2
						if self.is_valid_move_pawn(temp_position,temp_position2,piece):
							self.board[temp_position2.rank,temp_position2.file].valid_moves.append(piece.id)
					

	def evaluate_attacked_squares(self):
		temp_position = Position(0,0)
		for rank in range(8):
			for file in range(8):
				self.board[rank,file].is_attacked_by["white"] = []
				self.board[rank,file].is_attacked_by["black"] = []

		for rank in range(8):
			temp_position.rank = rank 
			for file in range(8):
				piece = self.board[rank,file].piece 
				temp_position.file = file 

				if piece.type == "pawn":
					self.evaluate_attacked_squares_pawn(temp_position,piece)
				elif piece.type == "rook":
					self.evaluate_attacked_squares_ranks_files(temp_position,piece)
				elif piece.type == "knight":
					self.evaluate_attacked_squares_knight(temp_position,piece)
				elif piece.type == "bishop":
					self.evaluate_attacked_squares_diagonals(temp_position,piece)
				elif piece.type == "queen":
					self.evaluate_attacked_squares_ranks_files(temp_position,piece)
					self.evaluate_attacked_squares_diagonals(temp_position,piece)
				elif piece.type == "king":
					self.evaluate_attacked_squares_king(temp_position,piece)

	def evaluate_attacked_squares_pawn(self,position,piece):
		temp_position = Position(0,0)
		direction = get_direction(piece.color)

		temp_position.rank = position.rank+direction*1
		temp_position.file = position.file+1
		if self.is_valid_position(temp_position):
			self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color].append(piece.id)

		temp_position.rank = position.rank+direction*1
		temp_position.file = position.file-1
		if self.is_valid_position(temp_position):
			self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color].append(piece.id)

	def evaluate_attacked_squares_ranks_files(self,position,piece):
		temp_position = Position(0,0)

		for rank in range(1,8):
			temp_position.rank = position.rank+rank
			temp_position.file = position.file
			if not self.determine_attackability(piece,temp_position):
				break

		for rank in range(1,8):
			temp_position.rank = position.rank-rank
			temp_position.file = position.file
			if not self.determine_attackability(piece,temp_position):
				break

		for file in range(1,8):
			temp_position.rank = position.rank
			temp_position.file = position.file+file
			if not self.determine_attackability(piece,temp_position):
				break

		for file in range(1,8):
			temp_position.rank = position.rank
			temp_position.file = position.file-file
			if not self.determine_attackability(piece,temp_position):
				break

	def evaluate_attacked_squares_knight(self,position,piece):
		temp_position = Position(0,0) 
		shifts = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

		for shift in shifts:
			temp_position.rank = position.rank+shift[0]
			temp_position.file = position.file+shift[1]
			if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.color != piece.color:
				self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color].append(piece.id)

	def evaluate_attacked_squares_diagonals(self,position,piece):
		temp_position = Position(0,0) 

		for rank in range(1,8):
			temp_position.rank = position.rank+rank
			temp_position.file = position.file+rank
			if not self.determine_attackability(piece,temp_position):
				break

		for rank in range(1,8):
			temp_position.rank = position.rank-rank
			temp_position.file = position.file-rank
			if not self.determine_attackability(piece,temp_position):
				break

		for file in range(1,8):
			temp_position.rank = position.rank-file
			temp_position.file = position.file+file
			if not self.determine_attackability(piece,temp_position):
				break

		for file in range(1,8):
			temp_position.rank = position.rank+file
			temp_position.file = position.file-file
			if not self.determine_attackability(piece,temp_position):
				break
			
	def determine_attackability(self,piece,position):
		if self.is_valid_position(position):
			temp_piece = self.board[position.rank,position.file].piece
			if temp_piece.type == "nopiece":
				self.board[position.rank,position.file].is_attacked_by[piece.color].append(piece.id)
				return True
			elif temp_piece.color != piece.color:
				self.board[position.rank,position.file].is_attacked_by[piece.color].append(piece.id)
				return False
			elif temp_piece.color == piece.color:
				return False
		else:
			return False

	def evaluate_attacked_squares_king(self,position,piece):
		temp_position = Position(0,0) 
		shifts = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,0)]
		opponent_color = get_opponent_color(piece.color)

		for shift in shifts:
			temp_position.rank = position.rank+shift[0]
			temp_position.file = position.file+shift[1]
			if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.color != piece.color and not self.board[temp_position.rank,temp_position.file].is_attacked_by[opponent_color]:
				self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color].append(piece.id)

	def update_board_encodings(self):
		encoded_board = self.encode_board()
		self.board_encodings.append(encoded_board)
		self.board_encodings = self.board_encodings[1:]

	def encode_board(self):
		encoded_board = ""
		for rank in range(8):
			for file in range(8):
				encoded_board += str(self.board[rank,file])
			encoded_board += "/"


	def clear_en_pessantability(self,turn_color):
		en_pessant_rank = 2
		if turn_color == "black":
			en_pessant_rank = 5
		for file in range(8):
			self.board[en_pessant_rank,file].is_en_pessantable_by[turn_color] = False

	def unhighlight_squares(self):
		for rank in range(8):
			for file in range(8):
				self.board[rank,file].is_highlighted = False

	def get_opponent_color(self, turn_color):
		if turn_color == "white":
			return "black"
		else: 
			return "white"

	def get_pawn_direction(self, turn_color):
		if turn_color == "white":
			return 1
		else: 
			return -1

	def reset(self):
		self.__init__()