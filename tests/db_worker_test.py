import pytest
from context import DataBase, User, Form, config

TEST_DB_PATH = "test.db"

def test_construct_class():
    with DataBase(db_location=TEST_DB_PATH):
        pass

@pytest.fixture()
def db():
    with DataBase(db_location=TEST_DB_PATH) as database:
        database.clear_all_tables()
        yield database

@pytest.mark.parametrize(
    "user",
    [
        User(chat_id=0),
        User(chat_id=1, state=config.States.DEFAULT.value),
        User(chat_id=2, state=config.States.ANSWERING_QUESTION.value, current_form="form", current_question=1),
    ]
)
def test_work_with_users_table(db, user):
    db.update_user(user)
    upd_user = db.get_user(user.chat_id)
    assert user.chat_id == upd_user.chat_id
    assert user.state == upd_user.state
    assert user.current_form == upd_user.current_form
    assert user.current_question == upd_user.current_question

@pytest.mark.parametrize("chat_id", [10])
def test_default_user_parameters(db, chat_id):
    user = db.get_user(chat_id)
    default_user = User(chat_id=chat_id)
    assert user.chat_id == default_user.chat_id
    assert user.state == default_user.state
    assert user.current_form == default_user.current_form
    assert user.current_question == default_user.current_question

@pytest.mark.parametrize(
    "form",
    [
        Form(form_id="empty"),
        Form(form_id="half_empty", creator_chat_id=10, questions_number=3),
        Form(form_id="half_full", creator_chat_id=15, questions_number=5, name="Simple name", description="Simple description"),
        Form(form_id="full", creator_chat_id=20, questions_number=7, name="Just name", description="Just descr", spreadsheet_id=10)
    ]
)
def test_work_with_forms_table(db, form):
    db.update_form(form)
    upd_form = db.get_form(form.form_id)
    assert form.form_id == upd_form.form_id
    assert form.creator_chat_id == upd_form.creator_chat_id
    assert form.questions_number == upd_form.questions_number
    assert form.name == upd_form.name
    assert form.description == upd_form.description
    assert form.spreadsheet_id == upd_form.spreadsheet_id
    db.delete_form(form.form_id)
    assert db.is_form_id_free(form.form_id)

@pytest.mark.parametrize("form_id", ["default"])
def test_default_form_parameters(db, form_id):
    form = db.get_form(form_id)
    default_form = Form(form_id=form_id)
    assert form.form_id == default_form.form_id
    assert form.creator_chat_id == default_form.creator_chat_id
    assert form.questions_number == default_form.questions_number
    assert form.name == default_form.name
    assert form.description == default_form.description
    assert form.spreadsheet_id == default_form.spreadsheet_id

@pytest.mark.parametrize(
    "form_id, question_id, messages",
    [
        ("form_1", 1, [1, 2, 3]),
        ("form_2", 1, [])
    ]
)
def test_work_with_qmessages_table(db, form_id, question_id, messages):
    for message_id in messages:
        db.insert_message_to_question(form_id=form_id, question_id=question_id, message_id=message_id)
    assert db.get_messages_id_from_question(form_id=form_id, question_id=question_id) == messages
    db.delete_questions_by_form_id(form_id)
    assert len(db.get_messages_id_from_question(form_id=form_id, question_id=question_id)) == 0

@pytest.mark.parametrize(
    "form_id, questions_number, answers, correct_result",
    [
        (
            "form_1",
            2,
            [
                (1, 0, "yes"),
                (2, 0, "no"),
                (2, 1, "great"),
                (1, 1, "ok"),
                (3, 0, "maybe")
            ],
            {
                1: ["yes", "ok"],
                2: ["no", "great"],
                3: ["maybe", None]
            }
        ),
        (
            "form_2",
            0,
            [],
            dict()
        )
    ]
)
def test_work_with_answers_table(db, form_id, questions_number, answers, correct_result):
    form = db.get_form(form_id)
    form.questions_number = questions_number
    db.update_form(form)
    for answer in answers:
        chat_id, question_id, answer_text = answer
        db.insert_answer(chat_id=chat_id, form_id=form_id, question_id=question_id, answer_text=answer_text)
    result = db.get_all_answers(form_id)
    assert result == correct_result
    db.delete_answers_by_form_id(form_id)

@pytest.mark.parametrize(
    "chat_id, forms, result",
    [
        (
            1,
            [
                Form(form_id="form_1", creator_chat_id=1),
                Form(form_id="form_2", creator_chat_id=1),
                Form(form_id="form_3", creator_chat_id=1)
            ],
            {"form_1", "form_2", "form_3"}
        ),
        (
            0,
            [],
            set()
        )
    ]
)
def test_user_forms(db, chat_id, forms, result):
    for form in forms:
        db.update_form(form)
    forms = db.get_user_forms(chat_id)
    assert set(forms) == result