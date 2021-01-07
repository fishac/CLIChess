from .Game.Game import Game

class CLIChess:
	def __init__(self,piece_display_type):
		self.piece_display_type = piece_display_type

	def run(self):
		play = True

		while play:
			game = Game(self.piece_display_type)
			game.play()

			while True:
				play_again = input("Play again? (y/n): ").lower()
				if play_again == "n":
					print("Thanks for playing!")
					play = False
					break
				elif play_again != "y":
					print("Please enter one of y or n.")
				else:
					break