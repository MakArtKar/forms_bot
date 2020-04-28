import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'api_key.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                 'https://www.googleapis.com/auth/drive'])

class Spreadsheet:

    def __init__(self, spreadsheet_id, service):
        self.data = []
        self.num = 1
        self.spreadsheet_id = spreadsheet_id
        self.service = service

    def post_answer(self, answer):
        answer = [str(x) for x in answer]
        self.data.append({
          'range': f'A{self.num}:{chr(65 + len(answer) - 1)}{self.num}',
          'majorDimension' : 'ROWS',
          'values' : [answer],
        })
        self.num += 1

    def post(self):
        return self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            'valueInputOption' : 'USER_ENTERED',
            'data' : self.data,
        }).execute()


def post_in_sheets(answers, spreadsheet_id):
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)


    ss = Spreadsheet(spreadsheet_id=spreadsheet_id, service=service)
    for answer in answers:
        ss.post_answer(answer)
    ss.post()
