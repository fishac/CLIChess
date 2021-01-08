from .Square import Square
from .Piece import Piece
from .Position import Position
from .BoardErrors import InvalidPositionError, NoPieceError, EmptySquareError, InvalidMoveError, InvalidPieceCheckError, InvalidCastleError
import copy
from numpy import ndarray

class Board:
	def __init__(self):
		self.board = ndarray((8,8),dtype=object)
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
			self.board[1,file] = Square(Position(1,file),Piece("pawn","white","p" + str(file) + "1"))
			self.board[6,file] = Square(Position(6,file),Piece("pawn","black","p" + str(file) + "6"))

		self.board[0,0] = Square(Position(0,0),Piece("rook","white","Ra1"))
		self.board[0,7] = Square(Position(0,7),Piece("rook","white","Rh1"))
		self.board[7,0] = Square(Position(7,0),Piece("rook","black","Ra8"))
		self.board[7,7] = Square(Position(7,7),Piece("rook","black","Rh8"))

		self.board[0,1] = Square(Position(0,1),Piece("knight","white","Nb1"))
		self.board[0,6] = Square(Position(0,6),Piece("knight","white","Ng1"))
		self.board[7,1] = Square(Position(7,1),Piece("knight","black","Nb8"))
		self.board[7,6] = Square(Position(7,6),Piece("knight","black","Ng8"))

		self.board[0,2] = Square(Position(0,2),Piece("bishop","white","Bc1"))
		self.board[0,5] = Square(Position(0,5),Piece("bishop","white","Bf1"))
		self.board[7,2] = Square(Position(7,2),Piece("bishop","black","Bc8"))
		self.board[7,5] = Square(Position(7,5),Piece("bishop","black","Bf8"))

		self.board[0,3] = Square(Position(0,3),Piece("queen","white","Qd1"))
		self.board[0,4] = Square(Position(0,4),Piece("king","white","Ke1"))
		self.board[7,3] = Square(Position(7,3),Piece("queen","black","Qd8"))
		self.board[7,4] = Square(Position(7,4),Piece("king","black","Ke8"))

		for file in range(8):
			for rank in range(4):
				self.board[rank+2,file] = Square(Position(rank+2,file),Piece("nopiece","none","np"))

		self.evaluate_attacked_squares()

	def highlight_possible_moves(self,position):
		if self.is_valid_position(position):
			piece = self.board[position.rank,position.file].piece
			if piece.type is not "nopiece":
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
					if piece_to_move.type is not "nopiece":
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
		if self.is_check(turn_color) and piece_to_move.type is not "king":
			raise InvalidPieceCheckError(piece_to_move.type)

		if piece_to_move.type is "pawn" :
			if end.rank is 0 or end.rank is 7:
				if promotion_type is "queen":
					piece_to_move.type = "queen"
				elif promotion_type is "rook":
					piece_to_move.type = "rook"
				elif promotion_type is "knight":
					piece_to_move.type = "knight"
				elif promotion_type is "bishop":
					piece_to_move.type = "bishop"
				else:
					raise InvalidPromotionTypeError(start,end)
				self.pieces[turn_color][promotion_type] += 1
				self.pieces[turn_color]["pawn"] -= 1
			elif abs(end.file-start.file) == 2:
				direction = 1
				en_pessantable_by = "black"
				if turn_color is "black":
					direction = -1
					en_pessantable_by = "white"
				self.board[start.rank+direction*1,start.file].is_en_pessantable_by[en_pessantable_by] = True

		if piece_to_take.type is not "nopiece":
			self.take_piece(piece_to_take,turn_color)

		if piece_to_move.type is "king":
			self.king_positions[turn_color] = copy.deepcopy(end)

		piece_to_move.position = copy.deepcopy(end)
		piece_to_move.has_moved = True
		self.board[end.rank,end.file].piece = copy.deepcopy(piece_to_move)
		self.board[start.rank,start.file].piece = Piece("nopiece","none","np")

	def castle(self,turn_color,direction):
		castle_rank = 0
		cross_check_color = "black"
		if turn_color is "black":
			castle_rank = 7
			cross_check_color = "white"

		king_position = self.king_positions[turn_color]
		if king_position == Position(castle_rank,4) and not self.board[king_position.rank,king_position.file].piece.has_moved:
			if direction is "short":
				corner_piece = self.board[castle_rank,7].piece
				inner_square_1 = self.board[castle_rank,5]
				inner_square_2 = self.board[castle_rank,6]
				if corner_piece.type is "rook" and corner_piece.has_moved is False and inner_square_1.piece.type is "nopiece" and not inner_square_1.is_attacked_by[cross_check_color] and inner_square_2.piece.type is "nopiece" and not inner_square_2.is_attacked_by[cross_check_color]:
					king = self.board[castle_rank,4]
					king.has_moved = True
					self.board[castle_rank,6].piece = copy.deepcopy(king)

					corner_piece.has_moved = True
					self.board[castle_rank,5].piece = copy.deepcopy(corner_piece)

					self.board[castle_rank,4].piece = Piece("nopiece","none")
					self.board[castle_rank,7].piece = Piece("nopiece","none")
				else:
					raise InvalidCastleError(turn_color)
			elif direction is "long":
				corner_piece = self.board[castle_rank,0].piece
				inner_square_1 = self.board[castle_rank,1]
				inner_square_2 = self.board[castle_rank,2]
				inner_square_3 = self.board[castle_rank,3]
				if corner_piece.type is "rook" and corner_piece.has_moved is False and inner_square_1.piece.type is "nopiece"  and not inner_square_1.is_attacked_by[cross_check_color] and inner_square_2.piece.type is "nopiece" and not inner_square_2.is_attacked_by[cross_check_color] and inner_square_3.piece.type is "nopiece" and not inner_square_3.is_attacked_by[cross_check_color]:
					king = self.board[castle_rank,4]
					king.has_moved = True
					self.board[castle_rank,2].piece = copy.deepcopy(king)

					corner_piece.has_moved = True
					self.board[castle_rank,3].piece = copy.deepcopy(corner_piece)

					self.board[castle_rank,4].piece = Piece("nopiece","none")
					self.board[castle_rank,0].piece = Piece("nopiece","none")
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
		if piece.type is "pawn":
			return self.is_valid_move_pawn(start,end,piece)
		elif piece.type is "rook":
			return self.is_valid_move_rook(start,end,piece)
		elif piece.type is "knight":
			return self.is_valid_move_knight(start,end,piece)
		elif piece.type is "bishop":
			return self.is_valid_move_bishop(start,end,piece)
		elif piece.type is "queen":
			return self.is_valid_move_queen(start,end,piece)
		elif piece.type is "king":
			return self.is_valid_move_king(start,end,piece)
		else:
			raise NoPieceError(start,piece.color)

	def is_valid_move_pawn(self,start,end,piece):
		direction = 1
		opponent_color = "black"
		if piece.color is "black":
			direction = -1
			opponent_color = "white"

		temp_position = Position(0,0)

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file
		if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.type is "nopiece" and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*2
		temp_position.file = start.file
		if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.type is "nopiece" and self.board[start.rank+direction*1,start.file].piece.type is "nopiece" and not piece.has_moved and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file-1
		if self.is_valid_position(temp_position) and piece.id in self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color] and self.board[temp_position.rank,temp_position.file].piece.color is opponent_color and end == temp_position:
			return True

		temp_position.rank = start.rank+direction*1
		temp_position.file = start.file+1
		if self.is_valid_position(temp_position) and piece.id in self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color] and self.board[temp_position.rank,temp_position.file].piece.color is opponent_color and end == temp_position:
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
		opponent_color = "black"
		if piece.color is "black":
			opponent_color = "white"
		return piece.id in self.board[end.rank,end.file].is_attacked_by[piece.color] and not self.board[end.rank,end.file].is_attacked_by[opponent_color]

	def take_piece(self,piece_to_take,piece_color):
		if piece_to_take.type is "pawn":
			self.pieces[piece_color]["pawns"] -= 1
		elif piece_to_take.type is "rook":
			self.pieces[piece_color]["rooks"] -= 1
		elif piece_to_take.type is "knight":
			self.pieces[piece_color]["knights"] -= 1
		elif piece_to_take.type is "bishop":
			self.pieces[piece_color]["bishops"] -= 1
		elif piece_to_take.type is "queen":
			self.pieces[piece_color]["queens"] -= 1

	def is_checkmate(self,turn_color):
		if self.is_check(turn_color):
			king_color = "white"
			if turn_color is "white":
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
					if self.is_valid_position(temp_position) and not self.board[temp_position.rank,temp_position.file].is_attacked_by[turn_color]:
						checkmate = False
						break
			return checkmate
		else:
			return False

	def is_check(self,turn_color):
		king_color = "white"
		if turn_color is "white":
			king_color = "black"
		king_position = self.king_positions[king_color]
		return self.board[king_position.rank,king_position.file].is_attacked_by[turn_color]
		
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

				if piece.type is "pawn":
					self.evaluate_attacked_squares_pawn(temp_position,piece)
				elif piece.type is "rook":
					self.evaluate_attacked_squares_ranks_files(temp_position,piece)
				elif piece.type is "knight":
					self.evaluate_attacked_squares_knight(temp_position,piece)
				elif piece.type is "bishop":
					self.evaluate_attacked_squares_diagonals(temp_position,piece)
				elif piece.type is "queen":
					self.evaluate_attacked_squares_ranks_files(temp_position,piece)
					self.evaluate_attacked_squares_diagonals(temp_position,piece)
				elif piece.type is "king":
					self.evaluate_attacked_squares_king(temp_position,piece)

	def evaluate_attacked_squares_pawn(self,position,piece):
		temp_position = Position(0,0)
		direction = 1
		if piece.color is "black":
			direction = -1

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
			if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.color is not piece.color:
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
			if temp_piece.type is "nopiece":
				self.board[position.rank,position.file].is_attacked_by[piece.color].append(piece.id)
				return True
			elif temp_piece.color is not piece.color:
				self.board[position.rank,position.file].is_attacked_by[piece.color].append(piece.id)
				return False
			elif temp_piece.color is piece.color:
				return False
		else:
			return False

	def evaluate_attacked_squares_king(self,position,piece):
		temp_position = Position(0,0) 
		shifts = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,0)]

		opponent_color = "black"
		if piece.color is "black":
			opponent_color = "white"

		for shift in shifts:
			temp_position.rank = position.rank+shift[0]
			temp_position.file = position.file+shift[1]
			if self.is_valid_position(temp_position) and self.board[temp_position.rank,temp_position.file].piece.color is not piece.color and not self.board[temp_position.rank,temp_position.file].is_attacked_by[opponent_color]:
				self.board[temp_position.rank,temp_position.file].is_attacked_by[piece.color].append(piece.id)

	def clear_en_pessantability(self,turn_color):
		en_pessant_rank = 1
		if turn_color is "black":
			en_pessant_rank = 6
		for file in range(8):
			self.board[en_pessant_rank,file].is_en_pessantable_by[turn_color] = False

	def unhighlight_squares(self):
		for rank in range(8):
			for file in range(8):
				self.board[rank,file].is_highlighted = False

	def reset(self):
		self.__init__()