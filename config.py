import enum
import os

BOT_TOKEN = os.getenv("FORMS_BOT_TOKEN")
DB_LOCATION = os.getenv("FORMS_BOT_DATABASE")

class States(enum.Enum):
    DEFAULT = 0
    MAKING_QUESTION = 1
    FORMS_NAME = 2
    FORMS_DESCRIPTION = 3
    ANSWERING_QUESTION = 4

