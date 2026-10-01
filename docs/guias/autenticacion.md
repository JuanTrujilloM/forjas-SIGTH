# Autenticación

Cómo entra la gente al SIGTH y qué decisiones hay detrás. Las reglas de fondo están en la
[documentación técnica §7](../DOCUMENTACION-TECNICA.md#7-seguridad-accesos-y-datos-personales);
acá va lo operativo.

## 1. Qué hace

El acceso es con **correo corporativo y contraseña**. No hay SSO, no hay auto-registro y
no hay recuperación pública de contraseña: las cuentas las crea TI. Esto cierra el
pendiente que preguntaba si la autenticación sería con contraseña propia o con el SSO de
la empresa.

El correo es el identificador: `User.USERNAME_FIELD` es `email` y el `username` que
traía `AbstractUser` se eliminó, para no tener dos identificadores conviviendo.

## 2. El dominio corporativo

Sale del `.env` como `CORPORATE_EMAIL_DOMAIN` (hoy `forjasbolivar.com`), sin el `@` y
sin quedar escrito en el código. Se valida en tres lugares, y solo los dos últimos son
control real:

| Dónde | Qué aporta |
|---|---|
| Formulario de Vue | Comodidad: avisa antes de gastar una petición |
| `LoginSerializer` | Rechaza el intento con un mensaje en español |
| Campo `email` del modelo | Impide **crear** la cuenta, también desde el admin |

El frontend lee el mismo dominio de `VITE_CORPORATE_EMAIL_DOMAIN`. Si cambia, hay que
cambiarlo en los dos `.env`: el del backend manda, el del frontend solo dibuja.

## 3. Endpoints

Todos cuelgan de `/api/auth/`.

| Método y ruta | Permiso | Para qué |
|---|---|---|
| `GET /api/auth/csrf/` | `AllowAny` | Entrega la cookie `csrftoken` que necesita el POST de ingreso |
| `POST /api/auth/login/` | `AllowAny` | Abre la sesión; devuelve el usuario |
| `POST /api/auth/logout/` | `IsAuthenticated` | Cierra la sesión; responde 204 |
| `GET /api/auth/me/` | `IsAuthenticated` | El frontend pregunta al arrancar si la cookie sigue viva |

**Un 403 en `me/` es la respuesta normal** para quien no ha entrado, no un fallo: el
store lo captura y manda a `/ingreso`. Aparece en rojo en la consola del navegador
porque DevTools pinta toda respuesta HTTP fallida, la maneje o no el JavaScript. Es 403
y no 401 porque DRF solo responde 401 cuando la clase de autenticación aporta cabecera
`WWW-Authenticate`, y `SessionAuthentication` no la tiene.

`LoginView` lleva `csrf_protect` explícito: DRF exime de CSRF a toda `APIView` y solo lo
exige cuando ya hay sesión, que es justo lo que el ingreso no tiene todavía.

Un correo desconocido, una contraseña equivocada y una cuenta desactivada devuelven
**el mismo mensaje**. Distinguirlos dejaría averiguar qué cuentas existen.

### Límite de intentos fallidos

Lo aplica `users/services/LoginAttemptService.py` desde `LoginSerializer`, con dos
contadores:

| Contador | Límite | Contra qué protege |
|---|---|---|
| Por correo | 5 fallos | Probar contraseñas contra una cuenta |
| Por IP | 20 fallos | Probar una contraseña común contra muchas cuentas |

- Al llegar a un límite, el ingreso responde **429** con "Demasiados intentos fallidos.
  Espera 15 minutos y vuelve a intentarlo." durante **15 minutos** desde el último fallo.
  El bloqueo se levanta solo; TI no tiene que hacer nada.
- Mientras dura, **ni la contraseña correcta entra**, y ni siquiera se comprueba: si se
  comprobara, el atacante sabría cuándo acertó.
- El límite por IP es más alto porque detrás de un NAT o un proxy varias personas
  comparten dirección.
- Un ingreso correcto reinicia el contador del correo, **no el de la IP**: si lo
  reiniciara, cualquiera con cuenta propia podría borrarlo entrando con ella.
- El correo se cuenta exista o no la cuenta, con la misma respuesta, para no revelar
  cuáles existen.
- Los contadores viven en la **caché de base de datos** (tabla `sigth_cache`, la crea la
  migración `users.0006`), compartida por todos los procesos del servidor. La caché en
  memoria que Django trae por defecto es una por proceso: con varios procesos el límite
  se multiplicaría y se reiniciaría con cada reinicio. En la tabla las claves van con
  hash: no guarda correos ni direcciones.
- La IP sale de `REMOTE_ADDR`. Si en producción hay un proxy inverso delante de Django,
  TI pone en `NUM_PROXIES` del `.env` cuántos hay; si no, todo el tráfico parecería venir
  del proxy. Con `0`, el valor por defecto, se ignora `X-Forwarded-For`, que el cliente
  puede falsificar para saltarse el límite.
- Para desbloquear a alguien antes de tiempo no hay pantalla: se vacía la caché con
  `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`, lo
  que reinicia todos los contadores.

## 4. La sesión

Cookie de sesión de Django, `httpOnly`, protegida por CSRF y revocable del lado del
servidor. El frontend no guarda ni escribe tokens.

Axios va con `withXSRFToken: true` además de `withCredentials`. Sin eso, desde Axios 1.6
la cabecera `X-CSRFToken` solo se manda al mismo origen: en producción backend y frontend
comparten dominio, pero en desarrollo Vite (5173) y Django (8000) son orígenes distintos
y **todo POST vuelve como 403 de `csrf_protect`**, con un cuerpo HTML que ni siquiera
trae `detail`.

## 5. Crear cuentas

No hay pantalla para esto: las crea TI desde el admin de Django, o por consola. La
contraseña **no se pasa por la línea de comandos**, porque quedaría en el historial del
shell y en la lista de procesos, así que se usa el modo interactivo:

```bash
cd backend && .venv/Scripts/python.exe manage.py createsuperuser
```

Pide el correo — que debe ser del dominio corporativo — y la contraseña sin mostrarla.
Para una cuenta de negocio, crearla en el admin y asignarle su **perfil** y, según el
perfil, su dirección (Director) o sus secciones (Líder). Sin perfil, la cuenta se trata
como de TI y la API no le devuelve empleados.

## 6. Lo que este módulo NO trae

- **No hay bloqueo permanente de cuenta.** El límite de intentos (§3) bloquea 15
  minutos y se levanta solo.
- **No hay recuperación de contraseña.** La pantalla solo remite a Recursos Humanos o TI.
- **No hay registro de los ingresos.** Queda `last_login`, nada más: no se guarda desde
  qué IP ni cuándo se falló.
- **No hay segundo factor.**

## 7. Migrar una base que ya tenga usuarios

La migración `users/0003` **elimina la columna `username`** y vuelve `email` único y
obligatorio. En una base con cuentas ya creadas hay que darle a cada una un correo
corporativo distinto **antes** de aplicarla, o la migración falla contra el índice único.
En la base de desarrollo actual no había cuentas de negocio, solo un superusuario de
prueba.
