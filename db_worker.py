from datetime import datetime
import logging
import sqlite3

import config


class User:
    def __init__(self, chat_id, state=config.States.DEFAULT.value, current_form=None, current_question=None):
        self.chat_id = chat_id
        self.state = state
        self.current_form = current_form
        self.current_question = current_question


class Form:
    def __init__(self, form_id, creator_chat_id=None, questions_number=None, name=None, description=None, spreadsheet_id=None):
        self.form_id = form_id
        self.creator_chat_id = creator_chat_id
        self.questions_number = questions_number
        self.name = name
        self.description = description
        self.spreadsheet_id = spreadsheet_id


class DataBase:
    def __init__(self, db_location=config.DB_LOCATION):
        self.__DB_LOCATION = db_location
        self.__db_connection = sqlite3.connect(self.__DB_LOCATION)
        self.__db_cursor = self.__db_connection.cursor()
        self.__create_table_if_not_exists()
    
    def __del__(self):
        self.__db_connection.close()

    def __enter__(self):
        return self
    
    def __exit__(self, ext_type, exc_value, traceback):
        self.__db_cursor.close()
        if isinstance(exc_value, Exception):
            self.__db_connection.rollback()
        else:
            self.__db_connection.commit()
        self.__db_connection.close()
    
    def close(self):
        self.__db_connection.close()

    def commit(self):
        self.__db_connection.commit()
    
    def __create_table_if_not_exists(self):
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
            chat_id INTEGER NOT NULL UNIQUE,
            state INTEGER,
            current_form TEXT,
            current_question INTEGER
        )""")
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS Forms(
            form_id TEXT NOT NULL UNIQUE,
            creator_chat_id INTEGER,
            questions_number INTEGER,
            name TEXT,
            description TEXT,
            spreadsheet_id INTEGER
        )""")
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS QMessages(
            form_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            inserted_time TIMESTAMP NOT NULL
        )""")
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS Answers(
            chat_id INTEGER NOT NULL,
            form_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            answer_text TEXT NOT NULL
        )""")
        self.commit()

    def clear_all_tables(self):
        self.__db_cursor.execute("DELETE FROM Users")
        self.__db_cursor.execute("DELETE FROM Forms")
        self.__db_cursor.execute("DELETE FROM QMessages")
        self.__db_cursor.execute("DELETE FROM Answers")
        self.commit()

    def __insert_user_if_not_in_db(self, chat_id):
        user = User(chat_id)
        self.__db_cursor.execute(
            "INSERT OR IGNORE INTO Users(chat_id, state, current_form, current_question) VALUES(?, ?, ?, ?)",
            (user.chat_id, user.state, user.current_form, user.current_question)
        )
    
    def __insert_form_if_not_in_db(self, form_id):
        form = Form(form_id)
        self.__db_cursor.execute(
            "INSERT OR IGNORE INTO Forms(form_id, creator_chat_id, questions_number, name, description, spreadsheet_id) VALUES(?, ?, ?, ?, ?, ?)",
            (form.form_id, form.creator_chat_id, form.questions_number, form.name, form.description, form.spreadsheet_id)
        )

    def insert_message_to_question(self, form_id, question_id, message_id):
        self.__db_cursor.execute(
            "INSERT INTO QMessages(form_id, question_id, message_id, inserted_time) VALUES(?, ?, ?, ?)",
            (form_id, question_id, message_id, datetime.now())
        )
        self.commit()

    def get_messages_id_from_question(self, form_id, question_id):
        self.__db_cursor.execute(
            "SELECT message_id FROM QMessages WHERE form_id=? and question_id=? ORDER BY inserted_time",
            (form_id, question_id)
        )
        items = self.__db_cursor.fetchall()
        messages_id = []
        for item in items:
            messages_id.append(item[0])
        return messages_id

    def delete_questions_by_form_id(self, form_id):
        self.__db_cursor.execute(
            "DELETE FROM QMessages WHERE form_id=?",
            (form_id,)
        )
        self.commit()

    def insert_answer(self, chat_id, form_id, question_id, answer_text):
        self.__db_cursor.execute(
            "INSERT INTO Answers(chat_id, form_id, question_id, answer_text) VALUES(?, ?, ?, ?)",
            (chat_id, form_id, question_id, answer_text)
        )
        self.commit()
    
    def delete_answers_by_form_id(self, form_id):
        self.__db_cursor.execute(
            "DELETE FROM Answers WHERE form_id=?",
            (form_id,)
        )
        self.commit()

    def get_user(self, chat_id):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute(
            "SELECT state, current_form, current_question FROM Users WHERE chat_id=?",
            (chat_id,)
        )
        items = self.__db_cursor.fetchall()
        state, current_form, current_question = items[0]
        return User(chat_id=chat_id, state=state, current_form=current_form, current_question=current_question)

    def update_user(self, user: User):
        self.__insert_user_if_not_in_db(user.chat_id)
        self.__db_cursor.execute(
            "UPDATE Users SET state=?, current_form=?, current_question=? WHERE chat_id=?",
            (user.state, user.current_form, user.current_question, user.chat_id)
        )
        self.commit()
    
    def is_form_id_free(self, form_id):
        self.__db_cursor.execute(
            "SELECT form_id FROM Forms WHERE form_id=?",
            (form_id,)
        )
        items = self.__db_cursor.fetchall()
        return len(items) == 0
    
    def get_form(self, form_id):
        self.__insert_form_if_not_in_db(form_id)
        self.__db_cursor.execute(
            "SELECT creator_chat_id, questions_number, name, description, spreadsheet_id FROM Forms WHERE form_id=?",
            (form_id,)
        )
        items = self.__db_cursor.fetchall()
        creator_chat_id, questions_number, name, description, spreadsheet_id = items[0]
        return Form(
            form_id=form_id,
            creator_chat_id=creator_chat_id,
            questions_number=questions_number,
            name=name,
            description=description,
            spreadsheet_id=spreadsheet_id
        )

    def update_form(self, form: Form):
        self.__insert_form_if_not_in_db(form.form_id)
        self.__db_cursor.execute(
            "UPDATE Forms SET creator_chat_id=?, questions_number=?, name=?, description=?, spreadsheet_id=? WHERE form_id=?",
            (form.creator_chat_id, form.questions_number, form.name, form.description, form.spreadsheet_id, form.form_id)
        )
        self.commit()
    
    def get_user_forms(self, chat_id):
        self.__db_cursor.execute(
            "SELECT form_id FROM Forms WHERE creator_chat_id=?",
            (chat_id,)
        )
        items = self.__db_cursor.fetchall()
        result = []
        for item in items:
            result.append(item[0])
        return result

    def delete_form(self, form_id):
        self.delete_questions_by_form_id(form_id)
        self.delete_answers_by_form_id(form_id)
        self.__db_cursor.execute(
            "DELETE FROM Forms WHERE form_id=?",
            (form_id,)
        )
        self.commit()

    def get_all_answers(self, form_id):
        self.__db_cursor.execute(
            "SELECT chat_id, question_id, answer_text FROM Answers WHERE form_id=?",
            (form_id,)
        )
        items = self.__db_cursor.fetchall()
        form = self.get_form(form_id)
        assert form.questions_number is not None
        result = dict()
        for item in items:
            chat_id, question_id, answer_text = item
            if chat_id not in result:
                result[chat_id] = [None] * form.questions_number
            result[chat_id][question_id] = answer_text
        return result 
