# SQL Server local en Windows 11

Cómo se montó el SQL Server de desarrollo en un PC con Windows, y los comandos del
día a día. Es el equivalente de [`sql-server-local.md`](sql-server-local.md), que
documenta el mismo montaje en macOS; lo que cambia entre los dos está señalado. La
base de producción todavía no está definida (la define TI): lo de acá replica lo que se
espera encontrar allá, no lo confirmado.

---

## 1. Por qué acá no hay que emular

En un Mac con Apple Silicon la imagen de SQL Server corre emulada, porque Microsoft
solo publica variante `amd64`. En este PC el procesador **es** x86-64, así que la
misma imagen corre nativa: no hace falta `--platform linux/amd64` y el rendimiento es
notablemente mejor.

Se verificó contra la instancia ya corriendo:

```
Microsoft SQL Server 2022 (RTM-CU26) (KB5093420) - 16.0.4265.3 (X64)
    Developer Edition (64-bit) on Linux (Ubuntu 22.04.5 LTS) <X64>
```

Mismo build que en el Mac, sin capa de emulación en medio.

El contenedor sigue siendo Linux: Docker Desktop lo ejecuta dentro de WSL 2. Eso es
un requisito, no un detalle — sin WSL 2 el motor de Linux no arranca.

---

## 2. Qué quedó instalado

| Componente | Versión | Dónde |
|---|---|---|
| Windows | 11 Pro 10.0.26200 | — |
| WSL | 2, distro Ubuntu | `wsl -l -v` |
| Docker | 29.5.3 | Docker Desktop |
| SQL Server | 2022 (RTM-CU26) 16.0.4265.3, Developer Edition | contenedor `sigth-sqlserver` |
| Collation del servidor | `Modern_Spanish_CI_AS` | — |
| msodbcsql18 | 18.6.2.1 | winget, `C:\Windows\System32\msodbcsql18.dll` |
| Python | 3.13.14 | `py --version` |
| Node / npm | 26.3.0 / 11.16.0 | cumple el `engines` del `package.json` |

**No se instalaron `mssql-tools18` ni `sqlcmd` en el host.** La imagen del contenedor
ya trae `sqlcmd` en `/opt/mssql-tools18/bin/`, y se usa vía `docker exec`. Es una
dependencia menos que mantener que en el Mac, donde vino por Homebrew.

La base se llama `sigth` y la aplicación se conecta con el login `sigth_app`,
**nunca con `sa`**.

---

## 3. Cómo se montó (para reproducirlo en otra máquina)

### 3.1 Driver ODBC 18

Windows ya trae un driver llamado `SQL Server`, pero es el legacy de hace veinte años
y **no sirve**: `mssql-django` necesita el 18. En PowerShell **como administrador**:

```powershell
winget install --id Microsoft.msodbcsql.18 -e --accept-package-agreements --accept-source-agreements
```

Cerrá y reabrí la terminal después, para que tome el PATH nuevo.

La verificación que vale es desde el mismo Python que usa Django, igual que en el Mac:

```powershell
backend\.venv\Scripts\python.exe -c "import pyodbc; print(pyodbc.drivers())"
```

La lista debe contener `ODBC Driver 18 for SQL Server`. Acá no existe el lío de las
dos instalaciones de ODBC que tiene macOS (Anaconda vs Homebrew): en Windows el
registro de drivers es único, en `HKLM:\SOFTWARE\ODBC\ODBCINST.INI`.

### 3.2 Contenedor

Reemplazá `PON_PASS_SA` por una contraseña de 8+ caracteres con al menos tres de estos
cuatro grupos: mayúsculas, minúsculas, dígitos y símbolos. Si no cumple, el contenedor
arranca, falla la inicialización y queda en bucle de reinicio.

```powershell
docker run -d --name sigth-sqlserver -e ACCEPT_EULA=Y -e 'MSSQL_SA_PASSWORD=PON_PASS_SA' -e MSSQL_COLLATION=Modern_Spanish_CI_AS -e MSSQL_PID=Developer -p 1433:1433 -v sigth-sqlserver-data:/var/opt/mssql --restart unless-stopped mcr.microsoft.com/mssql/server:2022-latest
```

Diferencias con el comando del Mac:

- **Sin `--platform linux/amd64`** — solo hacía falta por el Apple Silicon (§1).
- **Comillas simples** en el valor con contraseña. En PowerShell las dobles
  interpolan `$`, así que una contraseña con `$` se corrompería en silencio.

Qué hace cada bandera no obvia:

- `MSSQL_COLLATION` — **solo se aplica en el primer arranque, con el volumen vacío.**
  Cambiarlo después obliga a borrar el volumen y rehacer la base.
- `MSSQL_PID=Developer` — edición gratuita, funcionalmente equivalente a Enterprise,
  válida solo para desarrollo.
- `-v sigth-sqlserver-data:/var/opt/mssql` — sin el volumen, la base se pierde al
  recrear el contenedor.

`-p 1433:1433` publica el puerto en **todas** las interfaces, o sea que la base queda
alcanzable desde la red local. Para desarrollo conviene atarla a loopback con
`-p 127.0.0.1:1433:1433`. Se puede corregir después sin perder datos: `docker rm -f` y
volver a crear el contenedor reusando el mismo volumen no repite la inicialización.

### 3.3 Esperar a que termine la inicialización

**Este paso no existe en el doc del Mac y es donde más fácil se tropieza.** Con
`MSSQL_COLLATION` puesto, el primer arranque tiene dos fases: el motor levanta,
anuncia que está listo, y *después* reconstruye todas las bases de sistema para
aplicar el collation y se reinicia. En esa ventana de ~10 segundos las conexiones
fallan de forma engañosa (§5).

Este bucle reintenta hasta que el login funcione de verdad:

```powershell
$sa = Read-Host "Contrasena SA"
```

```powershell
do { Start-Sleep 5; docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $sa -C -Q "SELECT 1" *> $null } until ($?)
```

Lo que escribís en un `Read-Host` no queda en el historial, y las líneas que sí se
guardan contienen `$sa`, no el valor (§5).

### 3.4 Base de datos y usuario

Usá para `sigth_app` una contraseña **distinta** de la de `sa`: es la que termina en
`backend/.env` y la que usa Django todos los días.

```powershell
$app = Read-Host "Contrasena sigth_app"
```

```powershell
docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $sa -C -Q "CREATE DATABASE sigth;"
```

```powershell
docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $sa -C -Q "CREATE LOGIN sigth_app WITH PASSWORD = '$app', DEFAULT_DATABASE = sigth;"
```

```powershell
docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $sa -C -d sigth -Q "CREATE USER sigth_app FOR LOGIN sigth_app; ALTER ROLE db_owner ADD MEMBER sigth_app;"
```

`db_owner` está acotado a la base `sigth`, no al servidor, y Django lo necesita para
correr migraciones. **En producción se aprieta** a `db_ddladmin` + `db_datareader` +
`db_datawriter`, porque allá las migraciones las corre un despliegue controlado.

El `-C` de `sqlcmd` equivale a `TrustServerCertificate=yes`: el contenedor usa un
certificado autofirmado que el driver 18 rechazaría por defecto.

Comprobación:

```powershell
docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sigth_app -P $app -C -d sigth -Q "SELECT DB_NAME(), SUSER_NAME(), SERVERPROPERTY('Collation');"
```

Debe devolver `sigth`, `sigth_app` y `Modern_Spanish_CI_AS`.

### 3.5 Entorno virtual y dependencias

Se usa el intérprete del venv por ruta directa en vez de activarlo, para no depender
de la execution policy de PowerShell (§5):

```powershell
py -m venv backend\.venv
```

```powershell
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

```powershell
cd frontend; npm install
```

### 3.6 `.env` y migraciones

En `backend/.env` — **UTF-8 sin BOM** (§5):

```
SECRET_KEY=<generado abajo>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=sigth
DB_USER=sigth_app
DB_PASSWORD=<la del login sigth_app>
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_EXTRA_PARAMS=TrustServerCertificate=yes

CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
```

El `SECRET_KEY`:

```powershell
py -c "from secrets import token_urlsafe; print(token_urlsafe(50))"
```

En `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

Y las migraciones:

```powershell
cd backend; .venv\Scripts\python.exe manage.py migrate
```

---

## 4. Día a día

**Docker Desktop tiene que estar abierto.** A diferencia del Mac, en Windows no
arranca solo salvo que lo actives en Settings → General → *Start Docker Desktop when
you sign in*. El `--restart unless-stopped` solo revive el contenedor una vez que el
motor está arriba.

**Prender la base:**

```powershell
docker start sigth-sqlserver
```

**Apagarla** (los datos se conservan):

```powershell
docker stop sigth-sqlserver
```

**Ver si está corriendo:**

```powershell
docker ps --filter name=sigth-sqlserver
```

**Ver los logs** cuando algo no conecta:

```powershell
docker logs --tail 30 sigth-sqlserver
```

**Probar la conexión desde Django** — la prueba que más vale, porque recorre la misma
cadena que la aplicación:

```powershell
cd backend; .venv\Scripts\python.exe manage.py shell -c "from django.db import connection; c = connection.cursor(); c.execute('SELECT DB_NAME(), SUSER_NAME()'); print(c.fetchone())"
```

Debe imprimir `('sigth', 'sigth_app')`.

**Consultar la base a mano:**

```powershell
$app = Read-Host "Contrasena sigth_app"; docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sigth_app -P $app -C -d sigth -Q "SELECT name FROM sys.tables ORDER BY name;"
```

**Correr el backend:**

```powershell
cd backend; .venv\Scripts\python.exe manage.py runserver 8000
```

**Correr el frontend** (en otra terminal):

```powershell
cd frontend; npm run dev
```

**Comprobar que back y front se hablan:** con los dos corriendo, abrir
`http://localhost:5173/ingreso` e iniciar sesión. Si aún no hay ninguna cuenta, crearla
antes con `createsuperuser` (ver `docs/guias/autenticacion.md`).

**Después de traer cambios que tocan modelos:**

```powershell
cd backend; .venv\Scripts\python.exe manage.py migrate
```

**Empezar de cero** — borra la base entera, incluidos todos los datos:

```powershell
docker rm -f sigth-sqlserver; docker volume rm sigth-sqlserver-data
```

Después de eso hay que repetir §3.2, §3.3, §3.4 y `migrate`.

---

## 5. Trampas conocidas

**El contenedor dice estar listo antes de estarlo.** Es la trampa más costosa y la que
motivó §3.3. En el primer arranque con `MSSQL_COLLATION`, el log dice
`SQL Server is now ready for client connections` y acto seguido empieza a reconstruir
las bases de sistema. Un `sqlcmd` lanzado en esa ventana falla con dos errores seguidos
que apuntan en direcciones equivocadas:

```
Login failed for user 'sa'.
TCP Provider: Error code 0x2749.
A network-related or instance-specific error has occurred...
```

Parece contraseña mal puesta o puerto cerrado, y no es ninguna de las dos: el primer
error es el motor sin poder evaluar contraseñas todavía, el segundo es el reinicio
interno. La confirmación está en el log, buscando `Attempting to change default
collation` y `The default collation was successfully changed`. Usá el bucle de §3.3.

**El driver `SQL Server` que ya trae Windows no sirve.** Aparece en `Get-OdbcDriver` y
puede dar la falsa impresión de que no hay nada que instalar. Hay que instalar el 18
igual (§3.1).

**Las contraseñas quedan en el historial de PowerShell.** PSReadLine guarda cada línea
en texto plano en `ConsoleHost_history.txt`, y **persiste entre sesiones** — es peor
que el `~/.zsh_history` del Mac, porque sobrevive al reinicio sin que nadie lo piense.
Por eso todo en este documento usa `Read-Host` y variables. Si se te escapó una,
limpiala:

```powershell
$h = (Get-PSReadLineOption).HistorySavePath; (Get-Content $h) | Where-Object { $_ -notmatch 'MSSQL_SA_PASSWORD|sqlcmd' } | Set-Content $h -Encoding utf8
```

Y rotá la contraseña, que el historial no es el único sitio donde quedó:

```powershell
$nuevoSa = Read-Host "Nueva contrasena SA"; docker exec sigth-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $sa -C -Q "ALTER LOGIN sa WITH PASSWORD = '$nuevoSa';"
```

No hace falta tocar la variable `MSSQL_SA_PASSWORD` del contenedor: solo se lee en el
primer arranque con el volumen vacío, después queda inerte.

**El `.env` con BOM rompe la primera variable.** Si lo guardás desde el Notepad
eligiendo *UTF-8 con BOM*, `python-decouple` lee la primera clave con tres bytes basura
al principio y Django falla con un `SECRET_KEY` inexistente. Guardá como UTF-8 a secas.

**No actives el venv, usá el intérprete por ruta.** La execution policy por defecto de
Windows bloquea `Activate.ps1` con un error de scripts deshabilitados.
`backend\.venv\Scripts\python.exe` no pasa por ahí y funciona siempre.

**`manage.py dbshell` no funciona contra este contenedor.** Igual que en el Mac:
mssql-django construye la llamada a `sqlcmd` sin `-C`, así que el driver 18 rechaza el
certificado autofirmado. Peor: al fallar, Django imprime el comando completo en el
mensaje de error, **con la contraseña en texto plano**. Usá el `manage.py shell -c`
de §4.

**El collation no se puede cambiar después.** `MSSQL_COLLATION` solo actúa sobre un
volumen vacío. Si hay que cambiarlo, es borrar el volumen y rehacer todo.

**`TrustServerCertificate=yes` es solo para local.** En producción va vacío. Si se
cuela al servidor, se estaría cifrando contra un certificado sin validar.

**Finales de línea.** El repositorio no tiene `.gitattributes` y este PC tiene
`core.autocrlf=true`, así que git avisa `LF will be replaced by CRLF` al tocar archivos
que vienen del Mac. No corrompe nada — git normaliza a LF al commitear — pero si
aparecen diffs de archivos enteros sin cambios reales, es esto.