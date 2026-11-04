# 🛠️ Manual de Instalación y Despliegue

## 1. Descripción del Proyecto

Este documento describe el proceso de despliegue de la API NeoChaos, configurada en un clúster local de Alta Disponibilidad utilizando Docker Compose. La arquitectura incluye balanceo de carga, límites de recursos y observabilidad en tiempo real.

## 2. Arquitectura del Sistema

- **Proxy Inverso / Balanceador:** Nginx (Puerto 80)
- **Backend:** Flask + Gunicorn ([Número] réplicas, Puerto interno 5000)
- **Observabilidad:** Dozzle (Puerto 8080)
- **Pruebas de Carga:** Locust (Puerto 8089)

## 3. Prerrequisitos de Software

Antes de iniciar, asegúrese de tener instalado:

- **Docker Engine** (v20.10 o superior)
- **Docker Compose** (v2.0 o superior)
- **Git**
- Sistema Operativo: [Ej: Linux Ubuntu 22.04, Windows 11 con WSL2, etc.]

## 4. Pasos de Instalación

### Paso 1: Clonar el repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DE_LA_CARPETA]
```

### Paso 2: Configuración de Variables de Entorno (Si aplica)

Copie el archivo de ejemplo y configure las variables necesarias:

```bash
cp .env.example .env
# Edite el archivo .env con su editor de texto (nano, vim, etc.)
```

### Paso 3: Despliegue de la Infraestructura

Levante todos los servicios en segundo plano:

```bash
docker compose up --build -d
```

## 5. Verificación de Despliegue (Smoke Tests)

Ejecute los siguientes comandos para confirmar que el sistema está operativo:

**1. Verificar estado de contenedores:**

```bash
docker compose ps
```

_(Todos los contenedores deben mostrar estado `Up` y `healthy`)_

**2. Prueba de conectividad del API:**

```bash
curl -i http://localhost/health
```

_(Debe devolver `HTTP/1.1 200 OK`)_

**3. Acceso a Consolas de Administración:**

- Visor de Logs (Dozzle): Abrir `http://localhost:8080`
- Panel de Pruebas (Locust): Abrir `http://localhost:8089`

## 6. Comandos de Operación Diaria

- **Ver logs en terminal:** `docker compose logs -f api-backend`
- **Apagar el entorno:** `docker compose down`
- **Actualizar sin tiempo de inactividad (Zero-Downtime):**
  `docker compose up --build -d --no-deps --force-recreate api-backend`
