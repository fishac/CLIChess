from .Board.Board import Board
from .Board.BoardErrors import InvalidPositionError, NoPieceError, SameSquareError, InvalidMoveError, InvalidPieceCheckError, InvalidCastleError
from .Board.Position import Position
from .InputErrors import InvalidInputError, InvalidCastleInputError
import re
from os import system
from sys import stdout

class Game:
	def __init__(self):
		self.board = Board()
		stdout.reconfigure(encoding="utf-8")

	def play(self):
		game_end = False
		check_status = False
		checkmate_status = False

		while not game_end:
			self.display_board()

			if check_status:
				self.warn_check("white")

			self.move("white")

			checkmate_status = self.board.is_checkmate("black")
			if checkmate_status:
				game_end = True
				self.end_game("white")

			check_status = self.board.is_check("black")

			self.display_board()

			if check_status:
				self.warn_check("black")

			self.move("black")

			checkmate_status = self.board.is_checkmate("white")
			if checkmate_status:
				game_end = True
				self.end_game("black")

			check_status = self.board.is_check("white")

	def move(self,turn_color):
		while True:
			try:
				self.attempt_move(turn_color)
				break
			except InvalidInputError as e:
				print("Invalid input. Correct format \"startsquare endsquare\", or \"startsquare endsquare promotiontype\", \"castle direction\". Exs: \"a2 a4\", \"a7 a8 queen\", \"castle short\".\n")
			except InvalidPositionError as e:
				print("Invalid position: " + e.position + ". Files range from A to H, ranks range from 1 to 8.\n")
			except NoPieceError as e:
				print("Invalid move. No " + e.color + " piece at square " + e.position + ".\n")
			except SameSquareError as e:
				print("Invalid move. Cannot move a piece to the same square it is on.\n")
			except InvalidMoveError as e:
				print("Invalid move. Cannot move " + e.piece_type + " from " + e.start_position + " to " + e.end_position + ".\n")
			except InvalidPieceCheckError as e:
				print("Invalid move. Cannot move " + e.piece_type + " when in check.\n")
			except InvalidCastleInputError as e:
				print("Invalid input. Castling requires a direction, short (kingside) or long (queenside). Ex: \"castle short\".\n")
			except InvalidCastleError as e:
				print("Invalid move. Cannot castle.\n")

	def attempt_move(self,turn_color):
		inp = input(turn_color + " to play: ")
		inp_array = inp.split()
		position_regex = "[a-hA-H][1-8]"

		if inp_array[0].lower() is "castle":
			if len(inp_array) == 2:
				direction = inp_array[1]

				self.board.castle(turn_color, direction)
			else:
				raise InvalidCastleInputError(inp)
		elif len(inp_array) == 2 or len(inp_array) == 3:
			start_inp = inp_array[0]
			end_inp = inp_array[1]
			promotion_type = None
			if len(inp_array) == 3:
				promotion_type = inp_array[2].lower()

			if re.match(position_regex,start_inp):
				if re.match(position_regex,end_inp):
					start = Position(int(start_inp[1])-1,int(ord(start_inp[0])-96)-1)
					end = Position(int(end_inp[1])-1,int(ord(end_inp[0])-96)-1)
					try:
						self.board.make_move(start,end,turn_color,promotion_type)
					except:
						raise
				else:
					raise InvalidPositionError(end)
			else:
				raise InvalidPositionError(start)
		else:
			raise InvalidInputError(inp)

	def warn_check(self,color):
		print(color + " is in check.\n")

	def end_game(self,color):
		print("Checkmate, " + color + " wins.\n")

	def display_board(self):
		self.clear()

		print()

		string_to_print = "  "
		for i in range(41):
			string_to_print += "_"
		print(string_to_print)

		for rank in range(8):
			real_rank = 7-rank
			file = 0

			string_to_print = "  "
			for i in range(41):
				if i % 5 == 0:
					string_to_print += "|"
				else:
					string_to_print += " "
			print(string_to_print)

			string_to_print = str(real_rank+1) + " "
			for i in range(41):
				if i % 5 == 0:
					string_to_print += "|"
				elif i % 5 == 2:
					string_to_print += self.format_piece(real_rank,file)
					file += 1
				elif i % 5 == 1 or i % 5 == 3:
					string_to_print += " "
			print(string_to_print)

			string_to_print = "  "
			for i in range(41):
				if i % 5 == 0:
					string_to_print += "|"
				else:
					string_to_print += "_"
			print(string_to_print)

		string_to_print = "  "
		file = 0
		for i in range(41):
			if i % 5 == 2:
				string_to_print += chr(file + 97)
				file += 1
			else:
				string_to_print += " "
		print(string_to_print)

		print()

	def display_board2(self):
		self.clear()

		print()

		string_to_print = "  "
		for i in range(33):
			string_to_print += "_"
		print(string_to_print)

		for rank in range(8):
			real_rank = 7-rank
			file = 0

			string_to_print = "  "
			for i in range(33):
				if i % 4 == 0:
					string_to_print += "|"
				else:
					string_to_print += " "
			print(string_to_print)

			string_to_print = str(real_rank+1) + " "
			for i in range(33):
				if i % 4 == 0:
					string_to_print += "|"
				elif i % 4 == 2:
					string_to_print += self.format_piece2(real_rank,file)
					file += 1
				else:
					string_to_print += " "
			print(string_to_print)

			string_to_print = "  "
			for i in range(33):
				if i % 4 == 0:
					string_to_print += "|"
				else:
					string_to_print += "_"
			print(string_to_print)

		string_to_print = "  "
		file = 0
		for i in range(33):
			if i % 4 == 2:
				string_to_print += chr(file + 97)
				file += 1
			else:
				string_to_print += " "
		print(string_to_print)

		print()

	def format_piece(self,rank,file):
		piece_type = self.board.board[rank,file].piece.type
		piece_color = self.board.board[rank,file].piece.color
		formatted_color = piece_color[0]

		if piece_type is "nopiece":
			return "  "
		elif piece_type is "pawn":
			return formatted_color + "p"
		elif piece_type is "rook":
			return formatted_color + "R"
		elif piece_type is "knight":
			return formatted_color + "N"
		elif piece_type is "bishop": 
			return formatted_color + "B"
		elif piece_type is "queen": 
			return formatted_color + "Q"
		elif piece_type is "king":
			return formatted_color + "K"

	def format_piece2(self,rank,file):
		piece_type = self.board.board[rank,file].piece.type
		piece_color = self.board.board[rank,file].piece.color
		formatted_color = piece_color[0]

		if piece_type is "nopiece":
			return " "
		elif piece_color is "black":
			if piece_type is "pawn":
				return "\u2659"
			elif piece_type is "rook":
				return "\u2656"
			elif piece_type is "knight":
				return "\u2658"
			elif piece_type is "bishop": 
				return "\u2657"
			elif piece_type is "queen": 
				return "\u2655"
			elif piece_type is "king":
				return "\u2654"
		elif piece_color is "white":
			if piece_type is "pawn":
				return "\u265f"
			elif piece_type is "rook":
				return "\u265c"
			elif piece_type is "knight":
				return "\u265e"
			elif piece_type is "bishop": 
				return "\u265d"
			elif piece_type is "queen": 
				return "\u265b"
			elif piece_type is "king":
				return "\u265a"

	def reset(self):
		self.board.reset()

	def clear(self):
		system('clear')