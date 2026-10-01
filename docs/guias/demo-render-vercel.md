# Demostración en Render y Vercel

Cómo publicar una demostración del SIGTH para que Talento Humano lo pruebe. Vive solo en
la rama `demo/render`, que **nunca se fusiona en `develop`**: usa SQLite y datos
inventados, dos cosas que el sistema real no admite.

## 1. Qué es y qué no es

| | Demostración | Sistema real |
|---|---|---|
| Base de datos | SQLite, dentro del servidor de Render | SQL Server |
| Datos | Los de demostración: 78 empleados inventados y una cuenta por perfil | Los de Talento Humano |
| Dónde | Internet, en Render (API) y Vercel (pantallas) | Red interna, servidor de TI |
| Persistencia | **Se reinicia sola**: lo que se edite se pierde | Permanente |

- **Nunca se cargan datos reales**, ni siquiera unos pocos para probar: queda en internet
  y en servidores fuera de la empresa.
- **Los datos se reinician** cada vez que el servidor se duerme (tras unos 15 minutos sin
  uso) o se redespliega: el disco del plan gratuito de Render no se conserva. Cada visita
  empieza con los mismos datos limpios.
- **El primer ingreso tras una pausa tarda cerca de un minuto**, mientras Render despierta
  y vuelve a cargar los datos.
- **La búsqueda distingue tildes y mayúsculas acentuadas**: "gomez" o "GÓMEZ" no
  encuentran a "Gómez". Es una limitación de SQLite; en SQL Server sí los encuentra.
- **El admin de Django no está disponible**: Vercel solo reenvía `/api/` y el servidor no
  sirve los estilos del admin. Todo se prueba desde las pantallas; la cuenta de TI no
  tiene uso en la demostración.

## 2. Cómo está armado

```
Navegador ──> Vercel (sigth-demo.vercel.app)
                ├── /api/*  ──reenvía──> Render (sigth-demo-api.onrender.com) ── SQLite
                └── todo lo demás ──> el frontend compilado
```

El navegador solo ve el dominio de Vercel. Por eso la cookie de sesión funciona: si el
frontend llamara directamente a `onrender.com`, el navegador no la enviaría y nadie
podría entrar.

Los archivos de la rama:

| Archivo | Qué hace |
|---|---|
| `render.yaml` | Define el servicio de Render y sus variables |
| `backend/start-demo.sh` | En cada arranque: migra, recrea los datos de demostración y levanta gunicorn |
| `frontend/vercel.json` | Reenvía `/api/` a Render y manda las demás rutas al frontend |
| `backend/config/settings.py` | Con `DEMO_RENDER=True`: SQLite, HTTPS detrás del proxy de Render y su dominio permitido |
| `employees/serializers/EmployeePhotoUrlField.py` | Con `DEMO_RENDER=True`: URL de foto relativa, para que pase por Vercel con la cookie |

## 3. Montarla por primera vez

Hacen falta cuentas en [Render](https://render.com) y [Vercel](https://vercel.com),
conectadas a la cuenta de GitHub donde está el repositorio.

### 3.1 Render (la API)

1. **New → Blueprint**, elegir el repositorio y la rama **`demo/render`**. Render lee
   `render.yaml` y propone el servicio `sigth-demo-api`.
2. Llenar las variables que pide:
   - `DEMO_USERS_PASSWORD`: la contraseña de las cuentas de demostración, de al menos 12
     caracteres.
   - `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`: todavía no se conoce el dominio de Vercel;
     poner `pendiente.vercel.app` y `https://pendiente.vercel.app` y corregirlas en el
     paso 3.3.
3. Crear. La primera vez tarda unos minutos.
4. Anotar la URL del servicio. Si no quedó como `https://sigth-demo-api.onrender.com`
   (Render agrega un sufijo cuando el nombre está ocupado), cambiar el destino en
   `frontend/vercel.json`, hacer commit en `demo/render` y push.

### 3.2 Vercel (las pantallas)

1. **Add New → Project**, importar el repositorio.
2. **Root Directory**: `frontend`. Vercel detecta Vite solo.
3. **Environment Variables**:
   - `VITE_API_BASE_URL` = `/api`
   - `VITE_CORPORATE_EMAIL_DOMAIN` = `forjasbolivar.com`
4. Desplegar. Luego, en **Settings → Environments → Production**, poner **`demo/render`**
   como la rama de producción y volver a desplegar.
5. En **Settings → Git → Ignored Build Step**, elegir *Run my Bash script* con:

   ```bash
   [ "$VERCEL_GIT_COMMIT_REF" != "demo/render" ]
   ```

   Sin esto, Vercel compila también `develop` y cada `feature/*`, que no tienen
   `vercel.json` y no funcionarían.

### 3.3 Conectar las dos

En Render → el servicio → **Environment**, con el dominio real de Vercel (por ejemplo
`sigth-demo.vercel.app`):

- `ALLOWED_HOSTS` = `sigth-demo.vercel.app`
- `CSRF_TRUSTED_ORIGINS` = `https://sigth-demo.vercel.app`

Guardar: Render redespliega solo.

### 3.4 Comprobar

1. Despertar la API abriendo `https://<servicio>.onrender.com/api/auth/csrf/`. Cuando
   responda (puede tardar un minuto), seguir.
2. Abrir el dominio de Vercel y entrar con `demo.talento@forjasbolivar.com`.
3. Ver que el listado muestra empleados **con foto**, abrir un detalle y editar algo.

## 4. Lo que se le entrega a Talento Humano

- El enlace de Vercel.
- Las cuentas, una por perfil, para que vean cómo cambia lo que ve cada uno:

  | Cuenta | Perfil |
  |---|---|
  | `demo.talento@forjasbolivar.com` | Talento Humano: ve todo y edita |
  | `demo.gerencia@forjasbolivar.com` | Gerencia General: ve todo, solo lectura |
  | `demo.sst@forjasbolivar.com` | SST - SGI: todos los empleados, sin salario ni contacto |
  | `demo.director@forjasbolivar.com` | Director de Procesos Técnicos |
  | `demo.lider@forjasbolivar.com` | Líder de Calidad y Mantenimiento (dos secciones) |
  | `demo.coordinador@forjasbolivar.com` | Coordinador de Soldadura |

- La contraseña, **por un canal privado**, no en el mismo mensaje del enlace.
- Las advertencias de §1, en palabras simples: datos inventados, se reinician solos, el
  primer ingreso es lento y la búsqueda necesita las tildes.

## 5. Actualizar la demostración

Para llevarle a Talento Humano lo último de `develop`:

```bash
git switch demo/render
```

```bash
git merge develop
```

```bash
git push origin demo/render
```

Render y Vercel redespliegan solos. Si el merge da conflicto en `settings.py` o en
`EmployeePhotoUrlField.py`, conservar los bloques de `DEMO_RENDER` y lo nuevo de
`develop`.

## 6. Problemas comunes

| Síntoma | Causa | Qué hacer |
|---|---|---|
| La primera carga da error o se queda pensando | Render estaba dormido | Esperar un minuto y recargar; o despertarlo antes (§3.4) |
| Todo POST devuelve 403, incluido el ingreso | `CSRF_TRUSTED_ORIGINS` no tiene el dominio de Vercel | Corregirlo en Render (§3.3) |
| Respuestas 400 | `ALLOWED_HOSTS` no tiene el dominio de Vercel | Corregirlo en Render (§3.3) |
| Las pantallas cargan pero la API da 404 | El destino de `vercel.json` no es la URL real de Render | Corregirlo (§3.1, paso 4) |
| Nadie puede entrar: "Demasiados intentos fallidos" | El límite por IP. En la demo todos llegan desde la IP del proxy de Render, así que 20 fallos entre todos bloquean a todos 15 minutos | Render → **Manual Deploy → Restart service**: reinicia la base y los contadores |
| Las fotos no cargan | La URL de la foto salió absoluta | Revisar que `DEMO_RENDER` sea `True` en Render |
