import json
from locust import HttpUser, task, between, SequentialTaskSet

# -------------------------------------------------------
# COMPORTAMIENTO: Usuario Navegador (Tráfico Ligero GET)
# -------------------------------------------------------
class NavegadorTasks(SequentialTaskSet):
    @task
    def ver_catalogo(self):
        # Reemplaza '/api/productos' por la ruta GET real de tu API
        self.client.get("/api/productos", name="GET /api/productos")

    @task
    def ver_detalle_producto(self):
        # Consulta de producto individual
        self.client.get("/api/productos/1", name="GET /api/productos/:id")


class UsuarioNavegador(HttpUser):
    # Asigna el conjunto de tareas de navegación
    tasks = [NavegadorTasks]
    # Simula un tiempo de espera entre peticiones (1 a 3 segundos)
    wait_time = between(1, 3)
    # Proporción de peso para la simulación (ej. 3 navegadores por cada comprador)
    weight = 3


# -------------------------------------------------------
# COMPORTAMIENTO: Usuario Comprador (Tráfico Pesado POST)
# -------------------------------------------------------
class CompradorTasks(SequentialTaskSet):
    @task
    def realizar_compra(self):
        headers = {"Content-Type": "application/json"}
        payload = {
            "producto_id": 1,
            "cantidad": 2,
            "metodo_pago": "tarjeta"
        }
        # Reemplaza '/api/compras' por la ruta POST real de tu API
        self.client.post(
            "/api/compras",
            data=json.dumps(payload),
            headers=headers,
            name="POST /api/compras"
        )


class UsuarioComprador(HttpUser):
    tasks = [CompradorTasks]
    wait_time = between(0.5, 1.5)
    weight = 1