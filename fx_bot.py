import os
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.getenv("8605158805:AAEAGGiwaTXTxRg_JePzlhYzbCb4iLtBqHU")
CHAT_ID = os.getenv("625766912")

USD_THRESHOLD = 3.1
EUR_THRESHOLD = 3.55
BTC_THRESHOLD = 60000

CHECK_INTERVAL_SECONDS = 300
MORNING_HOUR = 8
MORNING_MINUTE = 30

TZ = ZoneInfo("Asia/Jerusalem")

last_daily_sent_date = None
usd_alert_sent = False
eur_alert_sent = False
btc_alert_sent = False


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": text},
        timeout=15
    )
    response.raise_for_status()


def get_live_rates():
    usd_response = requests.get(
        "https://api.frankfurter.dev/v1/latest?base=USD&symbols=ILS",
        timeout=15
    )
    usd_response.raise_for_status()
    usd = usd_response.json()["rates"]["ILS"]

    eur_response = requests.get(
        "https://api.frankfurter.dev/v1/latest?base=EUR&symbols=ILS",
        timeout=15
    )
    eur_response.raise_for_status()
    eur = eur_response.json()["rates"]["ILS"]

    btc_response = requests.get(
        "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        timeout=15
    )
    btc_response.raise_for_status()
    btc = float(btc_response.json()["data"]["amount"])

    return usd, eur, btc


def send_morning():
    usd, eur, btc = get_live_rates()
    send_telegram_message(
        f"💱 בוקר טוב\n"
        f"USD: {usd:.4f}\n"
        f"EUR: {eur:.4f}\n"
        f"BTC: {btc:,.2f} USD"
    )


def check():
    global usd_alert_sent, eur_alert_sent, btc_alert_sent

    usd, eur, btc = get_live_rates()

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

    if btc < BTC_THRESHOLD and not btc_alert_sent:
        send_telegram_message(f"⚠️ ביטקוין מתחת ל-{BTC_THRESHOLD}: {btc:,.2f} USD")
        btc_alert_sent = True
    elif btc >= BTC_THRESHOLD:
        btc_alert_sent = False


def main():
    global last_daily_sent_date

    while True:
        try:
            now = datetime.now(TZ)

            if (
                last_daily_sent_date != now.date()
                and (
                    now.hour > MORNING_HOUR
                    or (now.hour == MORNING_HOUR and now.minute >= MORNING_MINUTE)
                )
            ):
                send_morning()
                last_daily_sent_date = now.date()

            check()

        except Exception as e:
            try:
                send_telegram_message(f"❌ שגיאה בבוט: {e}")
            except Exception:
                pass

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
