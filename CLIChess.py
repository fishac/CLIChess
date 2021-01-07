from src.CLIChess import CLIChess

import sys
import getopt

def main(argv):
	if not argv:
		CLIChess("letters").run()
	elif len(argv) == 1:
		if argv[0] == "-p" or argv[0] == "--pieces":
			CLIChess("pieces").run()
		elif argv[0] == "-l" or argv[0] == "--letters":
			CLIChess("letters").run()
		else:
			print("Optional argument error. Use no arguments, argument -l, or argument --letters to use the letter-based pieces. Use argument -p or --pieces to use unicode character pieces.\n")
	else:
		print("Optional argument error. Use no arguments, argument -l, or argument --letters to use the letter-based pieces. Use argument -p or --pieces to use unicode character pieces.\n")

if __name__ == "__main__":
	main(sys.argv[1:])