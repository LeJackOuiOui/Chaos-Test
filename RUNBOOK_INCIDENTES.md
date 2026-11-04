# 🚨 Runbook de Operaciones e Incidentes (RAP 1)

**Propósito:** Guía de acción rápida para el equipo de Guardia/SRE frente a fallos en el entorno de producción local.

---

## 🛑 Incidente 1: Errores 502 Bad Gateway intermitentes o totales

**Descripción:** Los usuarios o Locust reportan picos de errores HTTP 502. Nginx está arriba pero no puede comunicarse con el backend.

### 🔍 Diagnóstico:

1. Revise el estado de salud de las réplicas:
   ```bash
   docker compose ps
   ```
   _(Identifique si los contenedores están `unhealthy` o `restarting`)_
2. Revise los logs del balanceador de carga:
   ```bash
   docker compose logs load-balancer --tail=20
   ```
   _(Busque el mensaje exacto, ej: `no live upstreams` o `Connection refused`)_

### 🛠️ Mitigación:

- **Si todos los upstreams están muertos (no live upstreams):** Verifique si Nginx los bloqueó. Asegúrese de que en `nginx.conf` el bloque upstream tenga `max_fails=0`. Reinicie Nginx: `docker compose restart load-balancer`.
- **Si un contenedor se apagó abruptamente:** Revise si fue por falta de memoria (Ver Incidente 2).

---

## 🛑 Incidente 2: Contenedores destruidos por falta de RAM (OOM Killed)

**Descripción:** Uno o varios contenedores se detienen repentinamente bajo carga. En Locust se ven caídas abruptas de conexiones.

### 🔍 Diagnóstico:

1. Verifique el consumo en tiempo real:
   ```bash
   docker stats
   ```
2. Revise los eventos del sistema Docker para confirmar el OOM:
   ```bash
   docker inspect [ID_DEL_CONTENEDOR_CAIDO] | grep -i oom
   ```

### 🛠️ Mitigación:

1. Ajuste el límite de memoria en `docker-compose.yml` del servicio afectado (Ej. pasar de `128M` a `256M`).
2. Aplique el cambio con un despliegue progresivo:
   ```bash
   docker compose up -d
   ```

---

## 🛑 Incidente 3: Tiempos de espera agotados (Worker Timeouts) y Latencia Alta

**Descripción:** Nginx devuelve 504 Gateway Timeout, o la latencia en Locust supera los [X] segundos. Los contenedores pueden marcarse como `unhealthy`.

### 🔍 Diagnóstico:

1. Abra Dozzle (`http://localhost:8080`) y filtre por la palabra `TIMEOUT` o `CRITICAL`.
2. Busque en los logs de Flask el mensaje: `[CRITICAL] WORKER TIMEOUT`.

### 🛠️ Mitigación:

1. Aumente temporalmente la cantidad de réplicas en `docker-compose.yml` para absorber la carga:
   ```yaml
   deploy:
     replicas: [Nuevo_Numero_Mayor]
   ```
2. Despliegue el cambio de escala:
   ```bash
   docker compose up -d
   ```
3. A largo plazo, el equipo de desarrollo debe optimizar las consultas lentas o cambiar Gunicorn a modo asíncrono.

---

## ⏪ Procedimiento de Emergencia: Rollback (Deshacer actualización)

Si una nueva versión (v2) causa un fallo crítico inmediato que no puede ser solucionado rápidamente:

1. Modifique el `docker-compose.yml` (o el `Dockerfile`) para apuntar de nuevo a la imagen/código de la versión anterior (v1).
2. Fuerce la recreación progresiva:
   ```bash
   docker compose up --build -d --no-deps --force-recreate api-backend
   ```
3. Verifique en Locust que la tasa de errores vuelva a 0%.
