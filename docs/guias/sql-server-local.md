# SQL Server local en macOS (Apple Silicon)

Cómo se montó el SQL Server de desarrollo en un Mac con chip Apple, y los comandos
del día a día. La base de producción todavía no está definida (pendiente 2 de la
[documentación técnica](../DOCUMENTACION-TECNICA.md#12-riesgos-deuda-técnica-y-pendientes)): lo de acá replica lo que se espera
encontrar allá, no lo confirmado.

---

## 1. Por qué hay que emular

SQL Server **no corre nativo en macOS** ni existe imagen de contenedor para ARM.
Se verificó contra el registro de Microsoft:

```
docker manifest inspect -v mcr.microsoft.com/mssql/server:2022-latest
  → "platform": { "architecture": "amd64", "os": "linux" }
```

Lo mismo para `2025-latest`. Ninguna de las dos publica variante `arm64`, así que en
un Mac con Apple Silicon el contenedor corre **emulado en amd64**, vía Rosetta 2
dentro de Docker Desktop. Funciona sin problemas para desarrollo; no esperes la
performance de un servidor real.

Por eso el `docker run` lleva `--platform linux/amd64`. Sin esa bandera, Docker
intenta resolver una imagen ARM que no existe y falla.

---

## 2. Qué quedó instalado

| Componente | Versión | Dónde |
|---|---|---|
| macOS | 26.6.2 | — |
| Docker | 29.4.1 | Docker Desktop |
| SQL Server | 2022 (RTM-CU26) 16.0.4265.3, Developer Edition | contenedor `sigth-sqlserver` |
| Collation del servidor | `Modern_Spanish_CI_AS` | — |
| msodbcsql18 | 18.6.2.1 | Homebrew (`microsoft/mssql-release`) |
| mssql-tools18 | 18.6.2.1 | Homebrew, provee `sqlcmd` y `bcp` |
| unixODBC | 2.3.14 | Homebrew |

La base se llama `sigth` y la aplicación se conecta con el login `sigth_app`,
**nunca con `sa`**.

---

## 3. Cómo se montó (para reproducirlo en otra máquina)

### 3.1 Driver ODBC

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
```

Homebrew 6 exige confiar explícitamente en los taps de terceros:

```bash
brew trust microsoft/mssql-release
```

```bash
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18
```

La verificación que vale es desde el mismo Python que usa Django:

```bash
cd backend && .venv/bin/python -c "import pyodbc; print(pyodbc.drivers())"
```

Debe imprimir `['ODBC Driver 18 for SQL Server']`.

### 3.2 Contenedor

Reemplazá `PON_PASS_SA` por una contraseña de 8+ caracteres con al menos tres de
estos cuatro grupos: mayúsculas, minúsculas, dígitos y símbolos. Si no cumple, el
contenedor arranca, falla la inicialización y queda en bucle de reinicio.

```bash
docker run -d --name sigth-sqlserver --platform linux/amd64 -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD='PON_PASS_SA' -e MSSQL_COLLATION=Modern_Spanish_CI_AS -e MSSQL_PID=Developer -p 1433:1433 -v sigth-sqlserver-data:/var/opt/mssql --restart unless-stopped mcr.microsoft.com/mssql/server:2022-latest
```

Qué hace cada bandera no obvia:

- `--platform linux/amd64` — obligatorio en Apple Silicon (§1).
- `MSSQL_COLLATION` — **solo se aplica en el primer arranque, con el volumen vacío.**
  Cambiarlo después obliga a borrar el volumen y rehacer la base.
- `MSSQL_PID=Developer` — edición gratuita, funcionalmente equivalente a Enterprise,
  válida solo para desarrollo.
- `-v sigth-sqlserver-data:/var/opt/mssql` — sin el volumen, la base se pierde al
  recrear el contenedor.

### 3.3 Base de datos y usuario

```bash
/opt/homebrew/opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P 'PON_PASS_SA' -C -Q "CREATE DATABASE sigth;"
```

```bash
/opt/homebrew/opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P 'PON_PASS_SA' -C -Q "CREATE LOGIN sigth_app WITH PASSWORD = 'PON_PASS_APP', DEFAULT_DATABASE = sigth;"
```

```bash
/opt/homebrew/opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P 'PON_PASS_SA' -C -d sigth -Q "CREATE USER sigth_app FOR LOGIN sigth_app; ALTER ROLE db_owner ADD MEMBER sigth_app;"
```

`db_owner` está acotado a la base `sigth`, no al servidor, y Django lo necesita para
correr migraciones. **En producción se aprieta** a `db_ddladmin` + `db_datareader` +
`db_datawriter`, porque allá las migraciones las corre un despliegue controlado.

El `-C` de `sqlcmd` equivale a `TrustServerCertificate=yes`: el contenedor usa un
certificado autofirmado que el driver 18 rechazaría por defecto.

### 3.4 `.env` y migraciones

En `backend/.env`:

```
DB_NAME=sigth
DB_USER=sigth_app
DB_PASSWORD=<la del login sigth_app>
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_EXTRA_PARAMS=TrustServerCertificate=yes
```

```bash
cd backend && .venv/bin/python manage.py makemigrations users employees
```

```bash
cd backend && .venv/bin/python manage.py migrate
```

---

## 4. Día a día

Docker Desktop tiene que estar abierto. El contenedor arranca solo con el sistema
(`--restart unless-stopped`), así que normalmente no hay que hacer nada.

**Prender la base:**

```bash
docker start sigth-sqlserver
```

**Apagarla** (los datos se conservan):

```bash
docker stop sigth-sqlserver
```

**Ver si está corriendo:**

```bash
docker ps --filter name=sigth-sqlserver
```

**Ver los logs** cuando algo no conecta:

```bash
docker logs --tail 30 sigth-sqlserver
```

**Probar la conexión desde Django** — la prueba que más vale, porque recorre la misma
cadena que la aplicación:

```bash
cd backend && .venv/bin/python manage.py shell -c "from django.db import connection; c = connection.cursor(); c.execute('SELECT DB_NAME(), SUSER_NAME()'); print(c.fetchone())"
```

Debe imprimir `('sigth', 'sigth_app')`.

**Consultar la base a mano** (reemplazá la contraseña):

```bash
/opt/homebrew/opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sigth_app -P 'PON_PASS_APP' -C -d sigth -Q "SELECT name FROM sys.tables ORDER BY name;"
```

**Correr el backend:**

```bash
cd backend && .venv/bin/python manage.py runserver 8000
```

**Correr el frontend** (en otra terminal):

```bash
cd frontend && npm run dev
```

**Comprobar que back y front se hablan:** con los dos corriendo, abrir
`http://localhost:5173/ingreso` e iniciar sesión. Si aún no hay ninguna cuenta, crearla
antes con `createsuperuser` (ver `docs/autenticacion.md`).

**Después de traer cambios que tocan modelos:**

```bash
cd backend && .venv/bin/python manage.py migrate
```

**Empezar de cero** — borra la base entera, incluidos todos los datos:

```bash
docker rm -f sigth-sqlserver && docker volume rm sigth-sqlserver-data
```

Después de eso hay que repetir §3.2, §3.3 y `migrate`.

---

## 5. Trampas conocidas

**Hay dos instalaciones de ODBC en la máquina.** `which -a odbcinst` devuelve el de
Anaconda (`/opt/homebrew/anaconda3/bin/odbcinst`, lee `/etc/odbcinst.ini`) y el de
Homebrew (`/opt/homebrew/bin/odbcinst`, lee `/opt/homebrew/etc/odbcinst.ini`). El de
Anaconda gana en el `PATH`, pero **el que importa es el de Homebrew**, porque es
contra el que está enlazado `pyodbc`. Si `odbcinst -q -d` dice
`Unable to find component name`, no significa que el driver falte: significa que
preguntaste a la instalación equivocada. Usá la ruta completa, o mejor
`pyodbc.drivers()`.

**El collation no se puede cambiar después.** `MSSQL_COLLATION` solo actúa sobre un
volumen vacío. Si hay que cambiarlo, es borrar el volumen y rehacer todo.

**`TrustServerCertificate=yes` es solo para local.** En producción va vacío. Si se
cuela al servidor, se estaría cifrando contra un certificado sin validar.

**`manage.py dbshell` no funciona contra este contenedor.** mssql-django construye la
llamada a `sqlcmd` sin `-C`, así que el driver 18 rechaza el certificado autofirmado
y la conexión falla. Peor: al fallar, Django imprime el comando completo en el
mensaje de error, **con la contraseña en texto plano**. Usá el `manage.py shell -c`
de §4 o `sqlcmd` con `-C` directamente.

**No pegar contraseñas en la línea de comandos.** Quedan en `~/.zsh_history` y son
visibles en la lista de procesos. Conviene cargarlas en una variable con
`read -rsp 'Contraseña: ' VAR` y usar `"$VAR"`.

---

## 6. Pendientes que afectan a este documento

| # | Qué falta | Impacto si difiere de lo de acá |
|---|---|---|
| 1 | Collation real de la instancia de producción | Ordenamiento y comparación de `ñ` y tildes. Búsquedas de apellidos que se comportan distinto |
| 2 | Versión real de SQL Server y sistema operativo del servidor | Se eligió 2022 por ser la más extendida on-premise; si TI tiene 2019, hay que verificarlo |

Ambos son parte del pendiente 2 de la documentación técnica y se cierran con
Infraestructura / TI. Al cerrarlos, actualizar la tabla de §2 y
eliminar la fila correspondiente.
