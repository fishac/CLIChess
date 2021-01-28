def get_opponent_color(color):
	if color == "white":
		return "black"
	else:
		return "white"

def get_direction(color):
	if color == "white":
		return 1
	else:
		return -1

def get_castle_rank(color):
	if color == "white":
		return 0
	else:
		return 7

def get_pawn_rank(color):
	if color == "white":
		return 1
	else:
		return 6