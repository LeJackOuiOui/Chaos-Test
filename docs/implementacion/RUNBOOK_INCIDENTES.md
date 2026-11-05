# 🚨 Runbook de Operaciones e Incidentes (RAP 1)

**Propósito:** Guía de acción rápida para diagnosticar y atender fallos en el entorno local de NeoChaos.

**Servicios del proyecto:**

- Balanceador Nginx: `load-balancer` (puerto `80`)
- API Flask/Gunicorn: `api-backend` (puerto interno `5000`)
- Visor de logs Dozzle: `log-viewer` (puerto `8080`)
- Pruebas de carga Locust: se ejecutan por separado, salvo que se agregue un servicio de Locust al Compose.

> **Importante:** Ejecute los comandos desde la carpeta donde se encuentra `docker-compose.yml`. Los comandos de esta guía están escritos para PowerShell y Docker Compose V2.

---

## 🛑 Incidente 1: Errores 502 Bad Gateway

**Descripción:** Nginx responde, pero no consigue comunicarse correctamente con la API.

### 🔍 Diagnóstico

1. Revise el estado de los contenedores:

   ```powershell
   docker compose ps -a
   ```

   Busque servicios detenidos, reiniciándose o que no estén saludables.

2. Consulte los últimos registros del balanceador:

   ```powershell
   docker compose logs --tail 50 load-balancer
   ```

3. Consulte los registros del backend:

   ```powershell
   docker compose logs --tail 50 api-backend
   ```

4. Compruebe que la configuración de Nginx sea válida:
   ```powershell
   docker compose exec load-balancer nginx -t
   ```

### 🛠️ Mitigación

- **Si el backend está detenido:** intente levantarlo:

  ```powershell
  docker compose up -d api-backend
  ```

- **Si se modificó `nginx.conf`:** primero valide la configuración con `nginx -t`. Si la validación es correcta, reinicie el balanceador:

  ```powershell
  docker compose restart load-balancer
  ```

- **Si el backend se detiene repetidamente:** revise el Incidente 2 (OOM Killed).

- **Si aparece `Connection refused`:** compruebe que el backend esté iniciado y escuchando en el puerto interno `5000`.

> **Nota sobre `max_fails`:** El `nginx.conf` actual ya contiene `max_fails=0`. No cambie ese valor como solución automática: desactiva el conteo de fallos del servidor upstream y no repara un backend detenido o inaccesible.

---

## 🛑 Incidente 2: Contenedores detenidos por falta de memoria (OOM Killed)

**Descripción:** Uno o varios contenedores se detienen durante una prueba de carga o al procesar solicitudes.

### 🔍 Diagnóstico

1. Observe el consumo de recursos:

   ```powershell
   docker stats
   ```

2. Identifique los contenedores y su estado:

   ```powershell
   docker compose ps -a
   ```

3. Copie el ID o nombre del contenedor afectado y consulte si Docker registró un OOM:
   ```powershell
   docker inspect --format "OOMKilled={{.State.OOMKilled}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}" ID_O_NOMBRE
   ```
   Reemplace `ID_O_NOMBRE` por el ID o nombre real del contenedor. Si muestra `OOMKilled=true`, Docker confirma que el contenedor fue terminado por falta de memoria.

### 🛠️ Mitigación

1. Abra `docker-compose.yml` y localice el servicio afectado. En la configuración actual, `api-backend` tiene un límite de memoria de `256M`.
2. Si las mediciones confirman que el límite es insuficiente y el equipo tiene memoria disponible, aumente el valor de forma controlada. Por ejemplo, puede probar `384M` y volver a medir.
3. Aplique el cambio recreando el servicio:
   ```powershell
   docker compose up -d --force-recreate api-backend
   ```
4. Compruebe el estado y el consumo:
   ```powershell
   docker compose ps
   docker stats
   ```

> No aumente los límites sin revisar primero la memoria disponible del equipo. Cambie únicamente el servicio que presenta el problema.

---

## 🛑 Incidente 3: Worker Timeouts, errores 504 y latencia alta

**Descripción:** Nginx devuelve `504 Gateway Timeout` o Locust registra tiempos de respuesta elevados.

### 🔍 Diagnóstico

1. Abra Dozzle en el navegador: `http://localhost:8080`.
2. Busque mensajes como `WORKER TIMEOUT` o `CRITICAL`.
3. También puede consultar los registros desde PowerShell:
   ```powershell
   docker compose logs --tail 100 api-backend
   docker compose logs --tail 100 load-balancer
   ```
4. Revise en Locust la latencia y el porcentaje de errores. Si Locust no está ejecutándose, inícielo según la práctica correspondiente.

### 🛠️ Mitigación

1. Si el backend está saturado, primero confirme el consumo con:

   ```powershell
   docker stats
   ```

2. Puede probar un aumento temporal de réplicas:

   ```powershell
   docker compose up -d --scale api-backend=6
   ```

3. Verifique cuántos contenedores quedaron activos:

   ```powershell
   docker compose ps
   ```

4. Vuelva a ejecutar la prueba de carga y compare los resultados.

> **Importante para esta versión del proyecto:** `nginx.conf` declara un único servidor upstream (`api-backend:5000`). No dé por hecho que aumentar las réplicas hará que Nginx distribuya automáticamente el tráfico entre todas ellas. Verifique la distribución antes de considerar resuelto el incidente. Si persiste la latencia, el equipo de desarrollo debe revisar las operaciones lentas y la configuración de Gunicorn/Nginx.

---

## ⏪ Procedimiento de emergencia: Rollback

**Cuándo utilizarlo:** Cuando una actualización reciente provoca un fallo crítico y no se puede corregir rápidamente.

### Pasos

1. Identifique el commit estable anterior:

   ```powershell
   git log --oneline -5
   ```

2. Cambie temporalmente a ese commit, reemplazando `COMMIT_ANTERIOR` por su identificador real:

   ```powershell
   git switch --detach COMMIT_ANTERIOR
   ```

3. Reconstruya y recree el backend con el código de esa versión:

   ```powershell
   docker compose up -d --build --no-deps --force-recreate api-backend
   ```

4. Verifique los servicios:

   ```powershell
   docker compose ps
   ```

5. Compruebe la API desde PowerShell:

   ```powershell
   Invoke-WebRequest -Uri http://localhost/health -UseBasicParsing
   ```

6. Ejecute nuevamente la prueba de Locust y confirme que los errores y la latencia regresaron a los valores esperados.

> **Precaución:** Este proyecto construye el backend desde el código local (`build: .`); por eso, reconstruir sin recuperar primero una versión anterior no constituye un rollback. Antes de cambiar de commit, guarde cualquier cambio local que no quiera perder. Después de validar el rollback, puede volver a su rama de trabajo con `git switch NOMBRE_DE_TU_RAMA`.

---

## ✅ Verificación rápida después de atender un incidente

Ejecute estos comandos:

```powershell
docker compose ps
Invoke-WebRequest -Uri http://localhost/health -UseBasicParsing
```

Confirme que los servicios estén activos, que `/health` responda correctamente y que Locust ya no reporte errores anormales.
