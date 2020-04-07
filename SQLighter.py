class User:
	pass

class Queston:
	pass

class Answers:
	pass

class SQLighter:
	# clas user = User
	def addUser(self, user):
		return User()

	def addQuestion(self, question):
		return Question()

	def addAnswer(self, answer):
		return Answer()

	def getUser(self, chat_id):
		return User()

	def getQuestion(self, form_id, question_id):
		return Question()

	def getAnswers(self, form_id):
		return Answer()
