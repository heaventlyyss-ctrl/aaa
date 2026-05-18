import asyncio
import json
import os
import gspread
from telegram import Bot
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ========== НАСТРОЙКИ ==========
TELEGRAM_BOT_TOKEN = "8633341618:AAE4rF2kdlo3uxZ1vNCjMCPEM6j5-qYo7vw"
TELEGRAM_CHAT_ID   = "697051704"
SPREADSHEET_URL    = "https://docs.google.com/spreadsheets/d/1gepN13SwdKtewNe1HLY-RLNWCZFBQ81GEppSjRmd5IE/edit"
SHEET_GID          = 31278572
INTERVAL_MINUTES   = 10
# ================================

def get_sheet_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    google_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if google_creds:
        creds_dict = json.loads(google_creds)
    else:
        with open("credentials.json", "r") as f:
            creds_dict = json.load(f)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(SPREADSHEET_URL)

    worksheet = None
    for sheet in spreadsheet.worksheets():
        if sheet.id == SHEET_GID:
            worksheet = sheet
            break

    if not worksheet:
        raise Exception(f"Лист с gid={SHEET_GID} не найден!")

    ba21 = worksheet.acell("BA21").value
    ba25 = worksheet.acell("BA25").value
    return ba21, ba25

async def send_report(bot: Bot):
    try:
        ba21, ba25 = get_sheet_data()
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        message = (
            f"📊 *Отчёт из Google Таблицы*\n"
            f"🕐 {now}\n\n"
            f"• BA21: `{ba21}`\n"
            f"• BA25: `{ba25}`"
        )
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
        print(f"[{now}] Отчёт отправлен ✅")
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    print("Бот запущен! Отправляю отчёт каждые", INTERVAL_MINUTES, "минут.")
    await send_report(bot)
    while True:
        await asyncio.sleep(INTERVAL_MINUTES * 60)
        await send_report(bot)

if __name__ == "__main__":
    asyncio.run(main())
