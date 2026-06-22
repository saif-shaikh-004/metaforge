import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "metaforge-500220-7a0ab3377853.json",   # your file name
    scope
)

client = gspread.authorize(creds)

sheet = client.open(
    "MetaForge"
).sheet1


def save_battle(row):
    sheet.append_row(row)

print("save_battle exists?", "save_battle" in globals())