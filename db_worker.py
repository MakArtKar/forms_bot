import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
		self.create_tables_if_not_exist()
				
	def create_tables_if_not_exist():
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
			chat_id int,
			state int,
			current_form text,
			current_question int,
		""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS Questions(
			form_id text,
			question_id int,
			message_id int,
			message_ord int
		""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS Answers(
			chat_id int,
			form_id text,
			question_id int,
			answer_text text
		""")
		self.connection.commit()

	def insert_user(self, chat_id, state, current_form, current_question):
		self.cursor.execute("INSERT INTO Users(chat_id, state, current_form, current_question) VALUES(?, ?, ?, ?)", (chat_id, state, current_form, current_question))
		self.connection.commit()

	def insert_question(self, form_id, question_id, message_id, message_ord):
		self.cursor.execute("INSERT INTO Questions(form_id, question_id, message_id, message_ord) VALUES(?, ?, ?, ?)", (form_id, question_id, message_id, message_ord))
		self.connection.commit()

	def insert_answer(self, chat_id, form_id, question_id, answer_text):
		self.cursor.execute("INSERT INTO Answers(chat_id, form_id, question_id, answer_text) VALUES(?, ?, ?, ?)", (chat_id, form_id, question_id, answer_text))
		self.connection.commit()

	def get_users_by_chat_id(self, chat_id):
		users = self.cursor.execute("SELECT chat_id, state, current_form, current_question FROM monitoring_rss WHERE chat_id = ?", (chat_id,)).fetchall()
		return users

	def get_messages_for_question(self, form_id, question_id):
		messages = self.cursor.execute("SELECT message_ord message_id FROM Questions WHERE form_id=? and question_id=?", (form_id, question_id))
		messages.sort()
		message_ids = [m[1] for m in messages]
		return message_ids

	def get_all_answers(self, form_id):
		return self.cursor.execute("SELECT chat_id, question_id, answer_text FROM Answers WHERE form_id=?", (form_id,)).fetchall()
