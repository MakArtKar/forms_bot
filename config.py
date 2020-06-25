import enum
import os


BOT_TOKEN = os.getenv("FORMS_BOT_TOKEN")
DB_LOCATION = os.getenv("FORMS_BOT_DATABASE")

class States(enum.Enum):
    DEFAULT = 0
    MAKING_QUESTION = 1
    ANSWERING_QUESTION = 2
    FORMS_NAME = 3
    FORMS_DESCRIPTION = 4
