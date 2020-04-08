class User:
	pass

class Form:
	pass

class Queston:
	pass

class Answers:
	pass

class SQLighter:
	def addUser(self, chat_id):
		return User()

	def addForm(self, form_id):  
		return Form()

	def addQuestion(self, form_id, question_id, message):
		return Question()

	def addAnswer(self, chat_answer_id, form_id, answers):
		return Answer()

	def getUser(self, chat_id):
		return User()

	def getForm(self, form_id):
		return Form()

	def getQuestion(self, form_id, question_id):
		return Question()

	def getAnswers(self, form_id):
		return Answer()
