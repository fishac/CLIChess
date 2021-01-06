class Piece:
	def __init__(self,piece_type,color):
		self.type = piece_type
		self.color = color
		self.has_moved = False
		self.is_en_pessantable = False