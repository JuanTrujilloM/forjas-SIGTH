# forjas-SIGTH

**SIGTH — Sistema de Información y Gestión de Talento Humano** de Forjas Bolívar.

Plataforma web interna que reemplaza el Excel de personal de Talento Humano. Cada persona
autorizada entra con su correo corporativo y ve directamente los empleados y los datos
que le corresponden según su perfil. Solo Talento Humano crea y edita.

| | |
|---|---|
| Backend | Django 5.2 + Django REST Framework, sobre SQL Server (`backend/`) |
| Frontend | Vue 3 + TypeScript + Vite (`frontend/`) |
| Estado | En desarrollo, entorno local |

## Arranque rápido (desarrollo)

Requisitos:
- Python 3.13;
- Node 22.18+ o 24.12+;
- Docker con SQL Server 2022;
- ODBC Driver 18 for SQL Server.

El montaje completo de la base está en
[`docs/guias/sql-server-local-windows.md`](docs/guias/sql-server-local-windows.md) (Windows) y
[`docs/guias/sql-server-local.md`](docs/guias/sql-server-local.md) (macOS).

1. Copie `backend/.env.example` a `backend/.env` y `frontend/.env.example` a
   `frontend/.env`, y llénelos.
2. Instale las dependencias y cree las tablas:

   ```powershell
   py -m venv backend\.venv
   backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
   cd backend; .venv\Scripts\python.exe manage.py migrate
   ```

3. Arranque el backend y el frontend, cada uno en su propia terminal:

   ```powershell
   cd backend; .venv\Scripts\python.exe manage.py runserver 8000
   ```

   ```powershell
   cd frontend; npm install; npm run dev
   ```

4. Abra <http://localhost:5173/ingreso>. Para tener datos y cuentas de prueba:

   ```powershell
   cd backend; .venv\Scripts\python.exe manage.py seed_demo_employees
   cd backend; .venv\Scripts\python.exe manage.py seed_demo_users
   ```

## Fotos de los empleados

Las fotos se guardan en la carpeta que indique `MEDIA_ROOT` en `backend/.env`; si queda
vacío, van a `backend/media/`. Por ahora se deja así: esa carpeta no se publica como ruta
pública, y las fotos solo salen por la API y por el admin, a quien tiene permiso de ver al
empleado. Cuando se monte en producción, TI define dónde vive esa carpeta y cómo se
respalda.

## Documentación

| Documento | Para qué |
|---|---|
| [`docs/DOCUMENTACION-TECNICA.md`](docs/DOCUMENTACION-TECNICA.md) | Documentación técnica y de traspaso a TI: arquitectura, API, seguridad, despliegue y operación |
| [`docs/adr/`](docs/adr/) | Decisiones técnicas y su porqué |
| [`docs/guias/`](docs/guias/) | Cómo funciona el ingreso y cómo montar SQL Server en Windows o macOS |
