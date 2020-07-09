import enum
import os

BOT_TOKEN = os.getenv("FORMS_BOT_TOKEN")
DB_LOCATION = os.getenv("FORMS_BOT_DATABASE")
FORM_ID_LEN = 12
REF = 'https://t.me/memorish_bot?start='


class States(enum.Enum):
    DEFAULT = 0
    MAKING_QUESTION = 1
    FORM_NAME = 2
    FORM_DESCRIPTION = 3
    ANSWERING_QUESTION = 4
    IMPORT_TO_GOOGLE_SHEETS = 5

