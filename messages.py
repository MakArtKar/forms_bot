import yaml

class Messages(object):
    def __init__(self, file_path: str):
        with open(file_path) as fin:
            text_data = fin.read()
        data = yaml.unsafe_load(text_data)
        self.my_forms = data["my_forms"]
        self.completed_form = data["completed_form"]
        self.start_complete_new_form_with_nondefault_state = data["start_complete_new_form_with_nondefault_state"]
        self.start_complete_new_form_with_answering_state = data["start_complete_new_form_with_answering_state"]
        self.start_complete_new_form_with_creating_state = data["start_complete_new_form_with_creating_state"]
        self.wrong_answer_format = data["wrong_answer_format"]
        self.button_new_form = data["button_new_form"]
        self.button_my_forms = data["button_my_forms"]
        self.choose_button = data["choose_button"]
        self.button_back = data["button_back"]
        self.forms_list_header = data["forms_list_header"]
        self.button_import_to_google = data["button_import_to_google"]
        self.button_delete_form = data["button_delete_form"]
        self.button_yes = data["button_yes"]
        self.button_no = data["button_no"]
        self.are_you_sure_to_delete_form = data["are_you_sure_to_delete_form"]
        self.type_google_sheet_link = data["type_google_sheet_link"]
        self.google_error_incorrect_link = data["google_error_incorrect_link"]
        self.google_error_permission = data["google_error_permission"]
        self.google_error_unknown = data["google_error_unknown"]
        self.google_import_ok = data["google_import_ok"]
        self.type_form_name = data["type_form_name"]
        self.type_form_description = data["type_form_description"]
        self.button_next_question = data["button_next_question"]
        self.button_end_form = data["button_end_form"]
        self.row_width_menu_creating_form = data["row_width_menu_creating_form"]
        self.type_first_question = data["type_first_question"]
        self.type_another_question = data["type_another_question"]
        self.created_form = data["created_form"]
