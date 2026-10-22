import time
import random
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return "OK", 200

# @app.route('/comprar', methods=['POST'])
# def comprar():
#     # time.sleep(0.2)
#     return "Compra realizada con éxito", 200

# @app.route("/error_aleatorio")
# def error_aleatorio():
#     if random.randint(1,5) == 1:
#         raise RuntimeError("Fallo de conexión simulado")
#     return "OK", 200

# @app.route("/memoria_ram")
# def fuga_ram():
#     data = []
#     for _ in range(1000000):
#         data.append("X" * 1000)
#     return "Procesado", 200

# @app.route("/version")
# def version():
#     return {
#         "version": "1.0.0",
#         "mensaje": "API v1 Operativa",
#     }, 200

@app.route("/aplicar-descuento", methods=['POST'])
def aplicar_descuento():
    time.sleep(1.2)
    return { "status": "Descuento aplicado", "descuento": 15 }, 200

if __name__ == '__main__':
    app.run(port=5000)