import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = "8605158805:AAEAGGiwaTXTxRg_JePzlhYzbCb4iLtBqHU"
CHAT_ID = "625766912"

USD_THRESHOLD = 10
EUR_THRESHOLD = 8

CHECK_INTERVAL_SECONDS = 300
MORNING_HOUR = 8
MORNING_MINUTE = 30

TZ = ZoneInfo("Asia/Jerusalem")

last_daily_sent_date = None
usd_alert_sent = False
eur_alert_sent = False


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})


def get_live_rates():
    usd = requests.get("https://api.frankfurter.dev/v1/latest?base=USD&symbols=ILS").json()["rates"]["ILS"]
    eur = requests.get("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=ILS").json()["rates"]["ILS"]
    return usd, eur


def send_morning():
    usd, eur = get_live_rates()
    send_telegram_message(f"💱 בוקר טוב\nUSD: {usd:.4f}\nEUR: {eur:.4f}")


def check():
    global usd_alert_sent, eur_alert_sent

    usd, eur = get_live_rates()

    if usd < USD_THRESHOLD and not usd_alert_sent:
        send_telegram_message(f"⚠️ דולר מתחת ל-{USD_THRESHOLD}: {usd:.4f}")
        usd_alert_sent = True
    elif usd >= USD_THRESHOLD:
        usd_alert_sent = False

    if eur < EUR_THRESHOLD and not eur_alert_sent:
        send_telegram_message(f"⚠️ אירו מתחת ל-{EUR_THRESHOLD}: {eur:.4f}")
        eur_alert_sent = True
    elif eur >= EUR_THRESHOLD:
        eur_alert_sent = False


def main():
    global last_daily_sent_date

    send_telegram_message("🚀 הבוט התחיל לעבוד")

    while True:
        now = datetime.now(TZ)

        if now.hour == MORNING_HOUR and now.minute == MORNING_MINUTE:
            if last_daily_sent_date != now.date():
                send_morning()
                last_daily_sent_date = now.date()

        check()
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
