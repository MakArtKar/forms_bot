from datetime import datetime
import logging
import sqlite3

class User:
	
	def __init__(self, chat_id, state = 0, current_form = None, current_question = None, forms_number = 0):
		self.chat_id = chat_id
		self.state = state
		self.current_form = current_form
		self.current_question = current_question
		self.forms_number = forms_number

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
			forms_number int
		""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS QMessages(
			form_id text,
			question_id int,
			message_id int,
			inserted_time timestamp
		""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS Answers(
			chat_id int,
			form_id text,
			question_id int,
			answer_text text
		""")
		self.connection.commit()

	def insert_user(self, user):
		self.cursor.execute("INSERT INTO Users(chat_id, state, current_form, current_question) VALUES(?, ?, ?, ?)", (user.chat_id, user.state, user.current_form, user.current_question, user.forms_number))
		self.connection.commit()

	def delete_user(self, chat_id):
		self.cursor.execute("DELETE FROM Users WHERE chat_id=?", (chat_id,))
		self.connection.commit()

	def get_user(self, chat_id):
		users_by_chat_id = self.cursor.execute("SELECT chat_id, state, current_form, current_question, forms_number FROM monitoring_rss WHERE chat_id = ?", (chat_id,)).fetchall()
		if not users_by_chat_id:
			user = User(chat_id=chat_id)
			insert_user(user)
			return user
		else:
			if len(users_by_chat_id) > 1:
				logging.error("More than one user with one chat_id in database")
			user_tuple = users_by_chat_id[0]
			user = User(chat_id=user_tuple[0], state=user_tuple[1], current_form=user_tuple[2], current_question=user_tuple[3], forms_number=user_tuple[4])
			return user

	def update_user(self, user):
		self.delete_user(user.chat_id)
		self.insert_user(user)

	def insert_message_to_question(self, form_id, question_id, message_id):
		self.cursor.execute("INSERT INTO Questions(form_id, question_id, message_id, inserted_time) VALUES(?, ?, ?, ?)", (form_id, question_id, message_id, datetime.now()))
		self.connection.commit()

	def get_messages_from_question(self, form_id, question_id):
		messages = self.cursor.execute("SELECT message_id FROM Questions WHERE form_id=? and question_id=? ORDER BY inserted_time", (form_id, question_id))
		return messages

	def insert_answer(self, chat_id, form_id, question_id, answer_text):
		self.cursor.execute("INSERT INTO Answers(chat_id, form_id, question_id, answer_text) VALUES(?, ?, ?, ?)", (chat_id, form_id, question_id, answer_text))
		self.connection.commit()

	def get_all_answers(self, form_id):
		return self.cursor.execute("SELECT chat_id, question_id, answer_text FROM Answers WHERE form_id=?", (form_id,)).fetchall()
