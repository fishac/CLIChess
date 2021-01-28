class Square:
	def __init__(self,position,piece):
		self.position = position
		self.piece = piece
		self.is_en_pessantable_by = {
			"white": False,
			"black": False
		}
		self.is_attacked_by = {
			"white": [],
			"black": []
		}
		self.valid_moves = []
		self.valid_moves_color = []
		self.is_highlighted = False

	def __str__(self):
		return "[" + str(self.position) + ":" + self.piece.id + ":" + str(self.is_en_pessantable_by["white"]) + ":" + str(self.is_en_pessantable_by["white"]) + "]"
		