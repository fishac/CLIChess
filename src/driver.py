from Game.Game import Game

def main():
	play = True

	while play:
		game = Game()
		game.play()

		while True:
			play_again = input("Play again? (y/n): ").lower()
			if play_again is "n":
				print("Thanks for playing!")
				play = False
			elif play_again is not "y":
				print("Please enter one of y or n.")

if __name__ == "__main__":
	main()