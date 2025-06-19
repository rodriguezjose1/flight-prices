from flask import Flask
import requests, os
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route("/")
def check_vuelo():
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    FLIGHTAPI_KEY = os.environ["FLIGHTAPI_KEY"]
    PRECIO_MAXIMO = int(os.environ.get("PRECIO_MAXIMO", "600"))

    def buscar_vuelo(origen="EZE", destino="LON"):
        fecha_desde = datetime.today().strftime("%Y-%m-%d")
        fecha_hasta = (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        url = f"https://flightapi.io/api/search"
        params = {
            "apikey": FLIGHTAPI_KEY,
            "from": origen,
            "to": destino,
            "departureDate": fecha_desde,
            "returnDate": "",
            "adults": 1,
            "currency": "USD",
            "limit": 1,
            "sortBy": "price",
        }
        r = requests.get(url, params=params)
        data = r.json()
        if "data" not in data or not data["data"]:
            return None
        vuelo = data["data"][0]
        return {
            "origen": origen,
            "destino": destino,
            "fecha": vuelo.get("departureDate", "Desconocida"),
            "precio": vuelo.get("price", 9999),
            "aerolinea": vuelo.get("airline", "Desconocida"),
        }

    def enviar_telegram(msg):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)

    vuelo = buscar_vuelo()
    if vuelo and vuelo["precio"] < PRECIO_MAXIMO:
        msg = (
            f"🎉 ¡Vuelo barato encontrado!\n"
            f"🛫 {vuelo['origen']} → {vuelo['destino']}\n"
            f"📅 {vuelo['fecha']}\n"
            f"✈️ Aerolínea: {vuelo['aerolinea']}\n"
            f"💰 ${vuelo['precio']} USD"
        )
        enviar_telegram(msg)
        return "Enviado ✅"
    return "Sin resultados 👀"


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
