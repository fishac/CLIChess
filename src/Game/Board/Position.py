class Position:
	def __init__(self,rank,file):
		self.rank = int(rank)
		self.file = int(file)

	def __eq__(self,other):
		return (self.rank,self.file) == (other.rank,other.file)