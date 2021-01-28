from .Board.Board import Board
from .Board.BoardErrors import InvalidPositionError, NoPieceError, EmptySquareError, SameSquareError, InvalidMoveError, InvalidPieceCheckError, InvalidCastleError
from .Board.Position import Position
from .InputErrors import InvalidInputError, InvalidCastleInputError, DeclinedDrawError
from .Utils import get_opponent_color
import re
from os import system
from sys import stdout

class Game:
	def __init__(self,piece_display_type):
		self.board = Board()
		self.piece_display_type = piece_display_type
		stdout.reconfigure(encoding="utf-8")

	def play(self):
		self.game_end = False
		self.check_status = False
		self.checkmate_status = False
		self.resign_status = False
		self.draw_status = False

		while not self.game_end:
			self.turn("white")

			if not self.game_end:
				self.turn("black")

	def turn(self,turn_color):
		opponent_color = get_opponent_color(turn_color)
		turn_complete = False
		while not turn_complete:
			self.display_board()
			self.board.unhighlight_squares()

			if self.draw_status or self.board.is_draw(turn_color):
				self.game_end = True
				self.draw()
				turn_complete = True
			else:
				if self.check_status:
					self.warn_check(turn_color)

				turn_complete = self.move(turn_color)

				if turn_complete:
					if self.resign_status:
						self.game_end = True
						self.resignation(opponent_color)

					self.checkmate_status = self.board.is_checkmate(turn_color)
					if self.checkmate_status:
						self.game_end = True
						self.checkmate(turn_color)

				self.check_status = self.board.is_check(opponent_color)

	def move(self,turn_color):
		end_of_turn = False
		while True:
			try:
				end_of_turn = self.attempt_move(turn_color)
				break
			except InvalidInputError as e:
				print("Invalid input. Correct format \"startsquare endsquare\", \"startsquare endsquare promotiontype\", \"castle direction\", \"resign\", \"?square\", or \"draw?\". Exs: \"a2 a4\", \"a7 a8 queen\", \"castle short\".\n")
			except InvalidPositionError as e:
				print("Invalid position: " + e.position + ". Files range from A to H, ranks range from 1 to 8.\n")
			except NoPieceError as e:
				print("Invalid move. No " + e.color + " piece at square " + e.position + ".\n")
			except EmptySquareError as e:
				print("There are no pieces at " + e.position + ".\n")
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
			except DeclinedDrawError as e:
				print(e.color + " declined the draw.\n")
		return end_of_turn

	def attempt_move(self,turn_color):
		inp = input(turn_color + " to play: ")
		inp_array = inp.lower().split()
		position_regex = "[a-hA-H][1-8]"

		if len(inp_array) != 0:
			if inp_array[0].lower() == "castle" and len(inp_array) == 2:
				if len(inp_array) == 2:
					direction = inp_array[1]

					self.board.castle(turn_color, direction)
					return True
				else:
					raise InvalidCastleInputError(inp)
			elif inp_array[0] == "resign" and len(inp_array) == 1:
				self.resign_status = True
				return True
			elif inp_array[0] == "draw?" and len(inp_array) == 1:
				try:
					self.attempt_draw(turn_color)
				except:
					raise
				return True
			elif inp_array[0][0] == "?" and len(inp_array[0]) == 3 and len(inp_array) == 1:
				position_inp = inp_array[0][1] + inp_array[0][2]
				if re.match(position_regex,position_inp):
					position = Position(int(position_inp[1])-1,int(ord(position_inp[0]))-97)
					try:
						self.board.highlight_possible_moves(position)
						return False
					except:
						raise
			elif len(inp_array) == 2 or len(inp_array) == 3:
				start_inp = inp_array[0]
				end_inp = inp_array[1]
				promotion_type = None
				if len(inp_array) == 3:
					promotion_type = inp_array[2].lower()

				if re.match(position_regex,start_inp):
					if re.match(position_regex,end_inp):
						start = Position(int(start_inp[1])-1,int(ord(start_inp[0]))-97)
						end = Position(int(end_inp[1])-1,int(ord(end_inp[0])-96)-1)
						try:
							self.board.make_move(start,end,turn_color,promotion_type)
							return True
						except:
							raise
					else:
						raise InvalidInputError(inp)
				else:
					raise InvalidInputError(inp)
			else:
				raise InvalidInputError(inp)

	def warn_check(self,color):
		print(color + " is in check.\n")

	def checkmate(self,color):
		print("Checkmate, " + color + " wins.\n")

	def resignation(self,color):
		print("Resignation, " + color + " wins.\n")

	def draw(self):
		print("Draw.\n")

	def attempt_draw(self,turn_color):
		opponent_color = get_opponent_color(turn_color)
		while True:
			draw_response = input(turn_color + " offers a draw. Does " + opponent_color + " accept? (y/n): ").lower()
			if draw_response == "n":
				raise DeclinedDrawError(opponent_color)
			elif draw_response == "y":
				self.draw_status = True
				break
			else:
				print("Please enter one of y or n.")

	def display_board(self):
		if self.piece_display_type == "pieces":
			self.display_board_pieces()
		elif self.piece_display_type == "letters":
			self.display_board_letters()

	def display_board_letters(self):
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
				elif i % 5 == 2:
					highlighted = self.board.board[real_rank,file].is_highlighted
					if highlighted:
						string_to_print += "o"
					else:
						string_to_print += " "
					file += 1
				else:
					string_to_print += " "
			print(string_to_print)

			file = 0
			string_to_print = str(real_rank+1) + " "
			for i in range(41):
				if i % 5 == 0:
					string_to_print += "|"
				elif i % 5 == 2:
					string_to_print += self.format_piece_letters(real_rank,file)
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

	def display_board_pieces(self):
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
				elif i % 4 == 2:
					highlighted = self.board.board[real_rank,file].is_highlighted
					if highlighted:
						string_to_print += "o"
					else:
						string_to_print += " "
					file += 1
				else:
					string_to_print += " "
			print(string_to_print)

			file = 0
			string_to_print = str(real_rank+1) + " "
			for i in range(33):
				if i % 4 == 0:
					string_to_print += "|"
				elif i % 4 == 2:
					string_to_print += self.format_piece_pieces(real_rank,file)
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

	def format_piece_letters(self,rank,file):
		piece_type = self.board.board[rank,file].piece.type
		piece_color = self.board.board[rank,file].piece.color
		formatted_color = piece_color[0]

		if piece_type == "nopiece":
			return "  "
		elif piece_type == "pawn":
			return formatted_color + "p"
		elif piece_type == "rook":
			return formatted_color + "R"
		elif piece_type == "knight":
			return formatted_color + "N"
		elif piece_type == "bishop": 
			return formatted_color + "B"
		elif piece_type == "queen": 
			return formatted_color + "Q"
		elif piece_type == "king":
			return formatted_color + "K"

	def format_piece_pieces(self,rank,file):
		piece_type = self.board.board[rank,file].piece.type
		piece_color = self.board.board[rank,file].piece.color
		formatted_color = piece_color[0]

		if piece_type == "nopiece":
			return " "
		elif piece_color == "black":
			if piece_type == "pawn":
				return "\u2659"
			elif piece_type == "rook":
				return "\u2656"
			elif piece_type == "knight":
				return "\u2658"
			elif piece_type == "bishop": 
				return "\u2657"
			elif piece_type == "queen": 
				return "\u2655"
			elif piece_type == "king":
				return "\u2654"
		elif piece_color == "white":
			if piece_type == "pawn":
				return "\u265f"
			elif piece_type == "rook":
				return "\u265c"
			elif piece_type == "knight":
				return "\u265e"
			elif piece_type == "bishop": 
				return "\u265d"
			elif piece_type == "queen": 
				return "\u265b"
			elif piece_type == "king":
				return "\u265a"

	def reset(self):
		self.board.reset()

	def clear(self):
		system('clear')