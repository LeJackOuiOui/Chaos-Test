from flask import Flask, jsonify, request
from mysql.connector import pooling

app = Flask(__name__)

# Configuración del Pool de Conexiones de MySQL
# (El pool es clave para resistir la carga de peticiones simultáneas de Locust)
db_config = {
    "host": "host.docker.internal",
    "user": "root",        # Cambia por tu usuario de MySQL
    "password": "",        # Cambia por tu contraseña de MySQL (si tiene)
    "database": "adso_db",
    "port": 3306
}

# Crear un pool de 10 conexiones reutilizables
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **db_config
)

def get_db_connection():
    return connection_pool.get_connection()

@app.route('/api/productos', methods=['GET'])
def get_productos():
    return jsonify([
        {"id": 1, "nombre": "Producto A", "precio": 100},
        {"id": 2, "nombre": "Producto B", "precio": 200}
    ]), 200

@app.route('/api/productos/<int:id>', methods=['GET'])
def get_producto_detalle(id):
    return jsonify({"id": id, "nombre": f"Producto {id}", "precio": 150}), 200

@app.route('/api/compras', methods=['POST'])
def crear_compra():
    data = request.get_json() or {}
    producto_id = data.get('producto_id', 1)
    cantidad = data.get('cantidad', 1)
    metodo_pago = data.get('metodo_pago', 'tarjeta')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO compras (producto_id, cantidad, metodo_pago) VALUES (%s, %s, %s)"
        cursor.execute(query, (producto_id, cantidad, metodo_pago))
        conn.commit()
        
        cursor.close()
        return jsonify({"message": "Compra registrada en MySQL con éxito"}), 201

    except Exception as e:
        # Aquí es donde se generarán los errores 500 cuando MySQL sature sus conexiones en la Fase 2
        return jsonify({"error": str(e)}), 500

    finally:
        if conn and conn.is_connected():
            conn.close() # Devuelve la conexión al pool

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)