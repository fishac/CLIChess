class InvalidMoveError(Exception):
	def __init__(self,piece_type,start,end):
		self.piece_type = piece_type
		self.start_position = convert_coordinate_to_position(start)
		self.end_position = convert_coordinate_to_position(end)

class NoPieceError(Exception):
	def __init__(self,position,color):
		self.position = convert_coordinate_to_position(position)
		self.color = color

class SameSquareError(Exception):
	def __init__(self,position):
		self.position = position

class InvalidPositionError(Exception):
	def __init__(self,position):
		self.position = convert_coordinate_to_position(position)

class InvalidPieceCheckError(Exception):
	def __init__(self,piece_type):
		self.piece_type = piece_type

class InvalidPromotionTypeError(Exception):
	def __init__(self,start,end):
		self.start_position = convert_coordinate_to_position(start)
		self.end_position = convert_coordinate_to_position(end)

class InvalidCastleError(Exception):
	def __init__(self,color):
		self.color = color

def convert_coordinate_to_position(position):
	return chr(position.file+97) + str(position.rank+1)