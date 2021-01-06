class Position:
	def __init__(self,rank,file):
		self.rank = rank
		self.file = file

	def __eq__(self,other):
		return (self.rank,self.file) == (other.rank,other.file)