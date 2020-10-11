import enum

FORM_ID_LEN = 12

class States(enum.Enum):
    DEFAULT = 0
    MAKING_QUESTION = 1
    FORM_NAME = 2
    FORM_DESCRIPTION = 3
    ANSWERING_QUESTION = 4
    IMPORT_TO_GOOGLE_SHEETS = 5
