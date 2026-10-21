from flask import Flask
import time
import requests

app = Flask(__name__)

@app.route("/comprar", methods=["POST"])
def procesar_compra():
# El desarrollador agregó una llamada a un servicio externo de validación de fraude
# Este servicio externo hipotético tarda 4 segundos en responder
    try:
# Simulación de llamada externa lenta
        time.sleep(4)
        return {"status": "Aprobado", "transaccion_id": 9942}, 200
    except Exception as e:
        app.logger.error(f"Fallo en pasarela de pagos: {str(e)}")
        return {"error": "Servicio no disponible"}, 500

if __name__ == '__main__':
    app.run(port=5000)