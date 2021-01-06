class InvalidInputError(Exception):
	def __init__(self,inp):
		self.inp = inp

class InvalidCastleInputError(Exception):
	def __init__(self,inp):
		self.inp = inp