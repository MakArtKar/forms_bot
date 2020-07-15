import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import *

CREDENTIALS_FILE = 'api_key.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                 'https://www.googleapis.com/auth/drive'])
class Spreadsheet:

    def __init__(self, spreadsheet_id, service):
        self.data = []
        self.spreadsheet_id = spreadsheet_id
        self.service = service

    def post_answer(self, answers):
        self.data.append({
          'range': 'A1',
          'majorDimension' : 'ROWS',
          'values' : answers,
        })

    def post(self):
        return self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            'valueInputOption' : 'USER_ENTERED',
            'data' : self.data,
        }).execute()


def map_to_list(answers):
    res = []
    for chat_id in answers:
        res.append(answers[chat_id])
    return res


def post_in_sheets(answers, spreadsheet_id):
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    ss = Spreadsheet(spreadsheet_id=spreadsheet_id, service=service)
    ss.post_answer(map_to_list(answers))
    ss.post()
