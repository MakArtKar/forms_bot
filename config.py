import enum
import os

token = os.getenv("FORMS_BOT_TOKEN")
db_path = os.getenv("FORMS_BOT_DATABASE")

class States(enum.Enum):
    DEFAULT = 0
    MAKING_QUESTION = 1
    ANSWERING_QUESTION = 2
