import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
sheets_service = build('sheets', 'v4', credentials=credentials)

def append_row(sheet_id, values, range_="Sheet1!A1"):
    body = {"values": [values]}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_,
        valueInputOption="RAW",
        body=body
    ).execute()

if __name__ == "__main__":
    append_row(GOOGLE_SHEET_ID, ["Hello", "from", "Google Sheets!"])
