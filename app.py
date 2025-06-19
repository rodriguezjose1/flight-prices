from flask import Flask
import requests
import os
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def check_vuelo():
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    FLIGHTAPI_KEY = os.environ["FLIGHTAPI_KEY"]
    PRECIO_MAXIMO = int(os.environ.get("PRECIO_MAXIMO", "600"))

    def buscar_vuelo(origen="EZE", destino="LON"):
        fecha = datetime.today().strftime("%Y-%m-%d")
        url = f"https://api.flightapi.io/onewaytrip/{FLIGHTAPI_KEY}/{origen}/{destino}/{fecha}/1/0/0/Economy/USD"

        try:
            r = requests.get(url)
            print("Status code:", r.status_code)
            if r.status_code != 200:
                print("Respuesta no exitosa:", r.text)
                return None

            data = r.json()
        except Exception as e:
            print("Error al llamar a la API:", e)
            return None

        try:
            itinerarios = data.get("itineraries", [])
            if not itinerarios:
                return None

            vuelo = itinerarios[0]
            precio = float(vuelo["pricing_options"][0]["price"]["amount"])
            aerolinea = vuelo["legs"][0]["segments"][0]["carrier"]["name"]
            fecha_salida = vuelo["legs"][0]["segments"][0]["departure"]

            return {
                "origen": origen,
                "destino": destino,
                "fecha": fecha_salida,
                "precio": precio,
                "aerolinea": aerolinea,
            }

        except Exception as e:
            print("Error procesando datos de vuelo:", e)
            return None

    def enviar_telegram(msg):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print("Error enviando mensaje a Telegram:", e)

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
