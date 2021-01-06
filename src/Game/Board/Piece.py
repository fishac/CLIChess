class Piece:
	def __init__(self,piece_type,color,unique_id):
		self.type = piece_type
		self.color = color
		self.has_moved = False
		self.id = unique_id