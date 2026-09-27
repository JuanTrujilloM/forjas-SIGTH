# CLAUDE.md — SIGTH

Guía de trabajo para el Sistema de Información y Gestión de Talento Humano (SIGTH) de
Forjas Bolívar S.A. Este documento manda sobre cualquier costumbre general: si algo de
acá contradice el estilo por defecto de una herramienta o de un asistente, gana lo de acá.

> **Documento reconstruido el 2026-09-07.** El original se perdió. La estructura se
> recuperó a partir de las referencias que el propio código dejó; el contenido de negocio
> se repuso con Juan. Todo lo marcado **`POR CONFIRMAR`** es un hueco real: no inventar el
> contenido, preguntarlo.

---

## 1. Propósito

Hoy toda la información del personal de Forjas Bolívar vive en **un archivo de Excel que
maneja la persona de Talento Humano**: los datos de cada empleado y los indicadores que
se calculan sobre ellos. Cuando alguien de otra dirección necesita un dato, le escribe a
esa persona y espera a que le responda. Talento Humano es el cuello de botella de toda
consulta de la empresa, y el archivo es un único punto de falla.

SIGTH reemplaza ese flujo por una plataforma donde:

- cada persona autorizada entra con **su correo corporativo y una contraseña**;
- **ve directamente la información que le corresponde, sin pedírsela a nadie**;
- lo que le corresponde lo decide **la dirección a la que pertenece**: solo ve los
  empleados que están bajo esa dirección;
- **Talento Humano ve a todos los empleados y es el único que modifica información.**

El problema que resuelve no es guardar datos: es **quitar el intermediario sin abrir la
información de más**. Por eso el control de acceso (§6) es el corazón del sistema y no
una funcionalidad más.

### 1.1 Alcance de esta fase

Dentro: consulta centralizada de los empleados, con el alcance recortado por dirección,
y la edición por parte de Talento Humano. Es decir, digitalizar el Excel actual y su uso.

**`POR CONFIRMAR`** — Qué procesos de talento humano entran después (nómina,
capacitaciones, dotación, ausentismo, evaluaciones) y cuáles quedan explícitamente
fuera. Los indicadores que hoy calcula el Excel también están sin definir.

---

## 2. Usuarios y alcance

- Sistema **interno**, no expuesto a internet público. Un solo cliente: el frontend Vue
  que se despliega junto al backend.
- Cada usuario de negocio tiene **un solo perfil** (`User.profile`). Qué empleados y qué
  columnas ve cada uno está en §6:
  - **Talento Humano** — solo el Jefe de Talento Humano. Ve todo y es el **único que
    crea y edita** empleados.
  - **Gerencia General** — el Gerente General. Ve todo, en solo lectura.
  - **SST - SGI** — el Líder de SST y el Analista SGI. Ven a todos los empleados, pero
    no todas las columnas.
  - **Director** — los directores de las 5 direcciones (el Gerente de Desarrollo de
    Negocios cuenta como director de Mercadeo y Ventas). Ven su dirección.
  - **Líder** — líderes, coordinadores y jefes de área (Jefe Planta, Jefe de
    Sostenibilidad). Ven las secciones que tienen a cargo, que pueden ser varias.
  - **TI** — cuenta sin perfil. Administra usuarios, direcciones y secciones desde el
    admin de Django, donde además ve a todos los empleados en solo lectura. Por la API
    no ve ninguno.
- Todo usuario de negocio es de **solo lectura** salvo Talento Humano.
- Los usuarios finales trabajan **siempre por el frontend**. El admin de Django es solo
  para Talento Humano y TI.
- Un usuario de negocio **no está enlazado a su registro de empleado**. Los datos de
  acceso (perfil, dirección, secciones) viven en la cuenta y los asigna TI.
- Las cuentas las crea TI. **No hay auto-registro** ni recuperación de contraseña
  pública.
- El identificador de acceso es el **correo corporativo**, no un nombre de usuario
  inventado: `User.USERNAME_FIELD` es `email` y `username` no existe (§5.1).
- El dominio corporativo sale del `.env` (`CORPORATE_EMAIL_DOMAIN`), no está escrito en
  el código, y se valida en el campo del modelo: una cuenta con un correo de fuera no
  se puede crear ni desde el admin.

**`POR CONFIRMAR`** — Volumen real de empleados, número de direcciones y usuarios
concurrentes esperados (§12 #3). Afecta al tamaño de página (§12 #5).

---

## 3. Arquitectura y stack

Monorepo con dos mitades independientes que solo se hablan por HTTP.

```
forjas-SIGTH/
├── backend/     Django + DRF, expone la API bajo /api/
├── frontend/    Vue 3 + Vite, único consumidor de esa API
└── docs/        documentación operativa (montaje, despliegue)
```

### 3.1 Backend

| Pieza | Elección | Por qué |
|---|---|---|
| Framework | Django 5.2 LTS | Admin listo para TI, auth y ORM maduros |
| API | Django REST Framework 3.18 | Viewsets y serializers como frontera de datos (§6.4) |
| Base de datos | SQL Server vía `mssql-django` + `pyodbc` | Es el motor que ya tiene la empresa |
| Filtros | `django-filter` | Filtrado declarativo sobre los viewsets |
| Auditoría | `django-simple-history` | §5.2 |
| Excel | `openpyxl` | Importar el archivo actual y exportar listados |
| Configuración | `python-decouple` | Todo lo que cambia entre entornos sale de `.env` |
| Lint | `flake8` | `backend/.flake8`, línea máx. 100 |

### 3.2 Frontend

| Pieza | Elección |
|---|---|
| Framework | Vue 3 (Composition API, `<script setup>`) + TypeScript |
| Build | Vite 8 |
| Estado | Pinia |
| Ruteo | Vue Router (`createWebHistory`) |
| HTTP | Axios, siempre a través de `BaseService` |
| Estilos | Bootstrap 5 (CSS global, sin framework de componentes propio) |
| Gráficas | Chart.js vía `vue-chartjs` — para los indicadores que hoy están en el Excel |
| Formato | Prettier (sin punto y coma, comillas simples, ancho 100) + ESLint flat config |

### 3.3 Reglas de arquitectura

- **No se agregan dependencias sin justificarlo.** Cada línea de `requirements.txt` y de
  `package.json` responde a una necesidad concreta del proyecto.
- El backend **no renderiza pantallas de negocio**. Los únicos templates que se
  renderizan son los del admin nativo de Django.
- El frontend **no habla con la base de datos** ni conoce su forma: solo consume la API.
- **El frontend nunca es la frontera de seguridad.** Ocultar un botón o una fila en Vue
  es comodidad de interfaz; lo que impide que un dato salga es el backend (§6.4).

---

## 4. Contrato entre backend y frontend

### 4.1 Rutas

- **Las rutas visibles al usuario van en español**: son las del frontend y las lee gente
  de la empresa. `/ingreso`, `/inicio`, `/empleados`, `/empleados/:id`.
- Los endpoints de la API van en inglés, igual que los identificadores del código:
  `/api/employees/`. No los ve el usuario final.
- Todo cuelga de `/api/`. **Sin prefijo de versión** (`/api/v1/`): el frontend es el único
  cliente y se despliega junto con el backend, así que no hay consumidores externos que
  romper.
- Cada app aporta su `urls.py` con un `DefaultRouter`, y `config/urls.py` los incluye.
- Rutas en minúscula, en plural, con barra final.
- Los nombres de ruta llevan el prefijo de la app: `name='users.auth_login'`.

### 4.2 Autenticación de las peticiones

Sesión de Django por cookie (§10.2). El frontend nunca guarda ni envía tokens.

### 4.3 Formato de respuestas

- JSON siempre. En producción el `BrowsableAPIRenderer` está apagado: renderizar datos de
  empleados como HTML fuera del frontend sería una fuga.
- Listados paginados con `PageNumberPagination`. `PAGE_SIZE` actual: 25 (§12 #5).
- Filtrado con `django-filter`; nunca armando querysets a mano desde parámetros crudos.
- **El alcance no es un filtro de la API**: se aplica siempre en el backend, venga o no
  un parámetro (§6.1). Un filtro que el cliente puede quitar no es control de acceso.
- Solo se puede filtrar y ordenar por columnas que el perfil puede ver (§6.2). Un filtro
  sobre una columna oculta se ignora.

### 4.4 CORS, orígenes y errores

- `CORS_ALLOWED_ORIGINS` se lee del `.env` y se enumera explícitamente.
  **Nunca `CORS_ALLOW_ALL_ORIGINS`, nunca un comodín.** En producción, con backend y
  frontend en el mismo dominio, la lista queda vacía.
- `CORS_ALLOW_CREDENTIALS = True`, porque la sesión viaja en cookie.
- `CSRF_TRUSTED_ORIGINS` también sale del `.env`.
- **Los mensajes de error que ve el usuario van en español.** DRF pone los errores que no
  son de campo en la clave `detail`; el frontend los lee de ahí, cae al primer error de
  campo cuando no hay `detail` (un rechazo de campo nunca llega a esa clave) y solo
  entonces usa un texto propio. Ese manejo vive en `BaseService.getApiErrorMessage()`
  y no se duplica en cada vista.
- Un usuario que pide un empleado fuera de su alcance recibe **404, no 403**: un 403
  confirmaría que ese empleado existe.

---

## 5. Modelo de datos

### 5.1 Entidades

La fuente es la especificación de Talento Humano ("Base de Datos Personal": campo, tipo,
lista de valores y quién lo ve) y el organigrama DR-DI-03. Ninguno de los dos entra al
repositorio (§11.2).

```
users                                           employees
Division ─1:N─ User ─1:N─ UserSection ─N:1─ Section      Position ─1:N─ Employee
   │                                            │         (cargo actual y anterior)
   └───────────────1:N──── Employee ────N:1─────┘         Employee ─1:N─ Employee (jefe)
                                                          Employee ─1:N─ ContractExtension
```

`users` — identidad y organización:

- **`Division`** — dirección de la empresa. Campos: `name` (único, ≤120), `is_active`.
  **Sin código**: la empresa no maneja uno. Carga inicial: las 5 direcciones de la
  especificación.
- **`Section`** — sección. Es lo que el negocio también llama **"proceso"**. Campos:
  `name` (único), `is_active`. **No cuelga de una dirección**: la especificación pide
  dirección y sección como dos datos independientes del empleado y no hay un cruce
  confirmado entre ambas. Carga inicial: las 35 secciones de la especificación.
- **`User`** — hereda de `AbstractUser`, pero **anula `username` y autentica por
  `email`** (`USERNAME_FIELD`), que es único y solo admite el dominio corporativo.
  Como `AbstractUser` crea usuarios por `username`, trae su propio `UserManager`
  (en `users/managers/`, no en `models/`: un manager no es un modelo). Agrega:
  - `profile` — perfil de acceso (`AccessProfile`, §6). Vacío = cuenta de TI.
  - `division` — FK, `PROTECT`. Obligatoria para el perfil Director.
  - `sections` — muchos a muchos con `Section` **a través de `UserSection`**.
    Obligatoria para el perfil Líder y prohibida para los demás.
- **`UserSection`** — qué secciones tiene a cargo un Líder. Una sección puede estar a
  cargo de varios (el coordinador y el jefe de encima). Es una **tabla intermedia
  explícita** y no la que Django crea sola, porque cada fila es una concesión de acceso:
  lleva timestamps, historial y `PROTECT`, que la automática no admite. Única por
  `(user, section)`.

`employees` — el dominio de talento humano:

- **`Position`** — cargo. Campos: `name` (único), `is_active`. Es tabla y no una lista
  fija porque la lista de la especificación está incompleta (faltan los cargos de
  directores, líderes y analistas, entre otros) y Talento Humano la completa desde el
  admin sin pasar por un despliegue. Carga inicial: los 31 cargos de la especificación.
- **`Employee`** — **un solo modelo, plano**, con una columna por dato del empleado: el
  espejo de la especificación. Los bloques de campos son los de §6.2. Relaciones:
  `division` (vacía para Gerencia y Junta Directiva, que no están en ninguna de las 5),
  `section`, `position`, `previous_position` e `immediate_boss` (otro empleado).
  - `status` (Activo / Retirado) **reemplaza a `is_active`**. Retirar es cambiar el
    estado; no se registra fecha ni motivo de retiro.
  - `id_number` es numérico y **único por sí solo**, sin importar el tipo de documento:
    quien pasa de T.I. a cédula con el mismo número conserva su registro.
  - Del cargo anterior se guarda **solo el último**, con sus fechas; no hay historial de
    cargos.
  - Solo son obligatorios estado, tipo y número de identificación y nombre (§12 #15).
  - Ciudad, municipio de nacimiento y nacionalidad son texto libre (§12 #16).
  - **Calculados, no se guardan**: edad, antigüedad y valor hora (salario / 210, que
    corresponde a la jornada de 42 horas semanales). Cumpleaños y vencimiento mes/año
    son solo el formato de fechas que ya existen y los arma el frontend. Guardarlos
    haría que se desactualicen solos, que es justo el problema del Excel.
- **`ContractExtension`** — prórroga de contrato. Un empleado puede tener varias. Campos:
  `employee`, `extension_date`; única por par.

Previstos en el diseño, fuera de esta fase:

- **Formación** — un catálogo de formaciones y una tabla intermedia empleado–formación con
  sus datos propios (fecha, por ejemplo). Espera la lista de SST (§12 #13).
- **Foto** — un campo de archivo en `Employee`. Espera que TI defina dónde se guardan los
  archivos (§12 #12).

### 5.2 Auditoría e historial

Llevan historial con `django-simple-history` — **queda registrado quién cambió qué y
cuándo** — estos modelos:

- `Employee` y `ContractExtension`: son datos de personas y la edición está concentrada
  en Talento Humano. Ante un reclamo hay que poder responder quién modificó un dato y en
  qué fecha, algo que el Excel actual no permite.
- `User` (sin `password` ni `last_login`) y `UserSection`: el perfil, la dirección y las
  secciones de una cuenta deciden qué datos de personas ve. Hay que poder responder
  quién le dio o le quitó acceso a alguien, y cuándo.

El `HistoryRequestMiddleware` está activo para que cada registro histórico sepa qué
usuario lo produjo.

**`POR CONFIRMAR`** — Cuánto tiempo se retiene el historial.

### 5.3 Convenciones de modelos

- **Un archivo por modelo**, nombrado igual que la clase en `PascalCase`
  (`users/models/User.py`), y reexportado desde `models/__init__.py` con `__all__`.
- `id = models.AutoField(primary_key=True)` explícito en cada modelo.
- `created_at` (`auto_now_add`) y `updated_at` (`auto_now`) en cada modelo, bajo un
  comentario `# timestamps`.
- Los campos se agrupan con comentarios: `# fields`, `# relations`, `# timestamps`.
- `verbose_name`, `verbose_name_plural` y `help_text` **en español**: es lo que ve TI en
  el admin.
- Los `choices` viven en `enums/`, no sueltos en el modelo.
- `Meta.ordering` siempre definido, para que la paginación sea estable.
- Borrado: `on_delete=models.PROTECT` por defecto. **No se borran registros de personas**:
  un empleado se retira con su `status`; los catálogos y las cuentas se desactivan con
  `is_active`.

---

## 6. Control de acceso

Es el corazón del sistema. Leerlo entero antes de tocar `users/access/`.

El acceso tiene dos ejes: **filas** (qué empleados ve un usuario) y **columnas** (qué
datos de esos empleados ve). Los dos los decide el **perfil** de la cuenta
(`User.profile`, §2). No los decide un permiso de Django ni un nombre de dirección
escrito en el código: los datos cambian y una constante mágica se desincroniza.

> Una versión anterior del diseño tenía una matriz de campos **por dirección**
> (`FIELD_ACCESS_MATRIX`), que se retiró cuando el alcance quedó solo por filas. La
> especificación de Talento Humano (septiembre de 2026) volvió a pedir el recorte por
> columnas, esta vez **por perfil**. La matriz vigente es la de §6.2; la anterior no se
> revive.

### 6.1 Filas: qué empleados ve cada perfil

| Perfil | Ve |
|---|---|
| Talento Humano | Todos |
| Gerencia General | Todos |
| SST - SGI | Todos |
| Director | Los de su dirección (`Employee.division` = `User.division`) |
| Líder | Los de sus secciones (`Employee.section` ∈ `User.sections`) |
| Sin perfil (TI) | Ninguno por la API; trabaja desde el admin |

- A los empleados sin dirección (Gerencia, Junta Directiva) solo los ven los tres
  perfiles que ven a todos.
- Un Director sin dirección o un Líder sin secciones no ve a nadie. El admin impide
  guardar una cuenta así, y la política lo trata igual por si una llega a existir.
- **Un usuario tiene un solo perfil.** El caso que lo pone a prueba es el Líder de SST,
  que es SST - SGI y a la vez tiene una sección a cargo: queda como SST - SGI y no ve el
  salario de su equipo. Combinar perfiles obligaría a decidir las columnas fila por fila
  y, ante la duda, no se expone (§10.1). Si hace falta, se cambia acá.
- El superusuario **no** tiene un atajo por la API. Un bypass por `is_superuser` sería
  una segunda regla que nadie recuerda revisar.

### 6.2 Columnas: qué datos ve cada perfil

Los campos de `Employee` se agrupan en bloques (`employees/enums/EmployeeFieldGroup.py`).
La matriz es la de la especificación de Talento Humano:

| Bloque | Campos | TH | Gerencia | Director / Líder | SST - SGI |
|---|---|:-:|:-:|:-:|:-:|
| Identidad | estado, tipo y número de identificación, nombre, fecha de nacimiento, edad, sexo, grupo sanguíneo, estado civil | ✔ | ✔ | ✔ | ✔ |
| Contacto y educación | hijos, celular, correo, dirección de residencia, barrio, ciudad, nivel educativo, título | ✔ | ✔ | ✔ | ✘ |
| Laboral | vinculación, categoría, dirección, grupo de evaluación, pacto colectivo, cargo actual y anterior con sus fechas, es líder, sección, centro de costos, área, rol adicional, jefe inmediato, fecha de ingreso, antigüedad | ✔ | ✔ | ✔ | ✔ |
| Salario y contrato | salario, tipo de salario, valor hora, auxilio de transporte, tipo de contrato, fecha de vencimiento, prórrogas, prórroga indefinido | ✔ | ✔ | ✔ | ✘ |
| Salud y riesgos | ARL, EPS | ✔ | ✔ | ✔ | ✔ |
| Pensión y cesantías | fondo de pensión, fondo de cesantías | ✔ | ✔ | ✔ | ✘ |
| Observaciones | alertas / observaciones | ✔ | ✔ | ✘ | ✘ |
| Sociodemográfico | municipio de nacimiento, nacionalidad, pertenencia étnica, composición familiar, personas a cargo, estrato | ✔ | ✔ | ✘ | ✔ |

- **Un campo que no esté en ningún bloque no lo ve nadie.** Agregar una columna al
  modelo no la publica hasta que alguien decide en qué bloque va.
- Una columna oculta **no sale en la respuesta** (la clave no viene, no llega en
  `null`), **no sirve para filtrar ni para ordenar** y no saldrá en las exportaciones.
  Si se pudiera filtrar por `estrato=1`, el estrato se deduciría aunque no se muestre.

### 6.3 Escritura

- **Solo Talento Humano crea y edita**, por la API y por el admin. Todos los demás son de
  solo lectura. Se niega el método en el backend, no se ocultan botones.
- **Nadie borra empleados.** Un empleado se retira cambiando su estado.
- En el admin: Talento Humano (con `is_staff`) crea y edita empleados y cargos. TI ve a
  los empleados en solo lectura. Nadie más entra a esa parte del admin. Lo decide la
  misma política, no los permisos de modelo de Django.

### 6.4 Dónde vive la decisión

- **Un único punto decide cada eje.** Ningún endpoint resuelve por su cuenta a quién o
  qué puede ver; todos preguntan a la misma política.
- Las filas se recortan en **`get_queryset()`**, no en el serializer ni en el frontend:
  si el registro no está en el queryset, no sale por ninguna ruta, ni siquiera pidiendo
  el detalle por `id` a mano. Un empleado fuera de alcance responde **404, no 403**.
- Las columnas se recortan en el **serializer**, y los filtros, el orden y la búsqueda
  se restringen a las columnas visibles.
- Los serializers listan sus campos explícitamente. **Nunca `fields = '__all__'`.**

En el código, en `users/access/`:

- **`EmployeeScopePolicy`** — decide las filas. `scope(user, queryset, division_lookup,
  section_lookup)` devuelve el queryset ya recortado; `sees_every_employee(user)`
  responde si el perfil ignora el recorte.
- **`EmployeeFieldPolicy`** — decide las columnas y la escritura.
  `readable_fields(user)` devuelve los campos visibles; `can_write(user)` y
  `can_view_admin(user)` responden por la edición y por el admin.
- **`EmployeeScopedMixin`** — aplica las filas. Se antepone al viewset y llama a la
  política dentro de `get_queryset()`. Sus atributos `division_lookup` y
  `section_lookup` cubren un modelo que llegue a `Division` o a `Section` por una
  relación indirecta.
- **`EmployeeFieldsMixin`** — aplica las columnas. Se antepone al serializer y descarta
  los campos que el perfil no ve.
- **`EmployeeFieldFilterSet`**, **`EmployeeFieldOrderingFilter`** y
  **`EmployeeFieldSearchFilter`** — aplican las columnas a los filtros, al orden y a la
  búsqueda.
- **`EmployeeWritePermission`** — aplica la escritura en las vistas.

**Hay dos formas de romper el acceso, y por eso se revisan en cada vista y serializer
nuevos:** una vista que sobreescriba `get_queryset()` sin llamar a `super()` se salta
las filas, y un serializer de `Employee` que no herede `EmployeeFieldsMixin` se salta
las columnas.

---

## 7. Convenciones del backend

### 7.1 Estructura de cada app

```
<app>/
├── enums/          choices y constantes
├── filters/        filtersets de django-filter, uno por archivo
├── managers/       managers de modelo
├── migrations/
├── models/         un archivo por modelo
├── serializers/    un archivo por serializer
├── services/       lógica de negocio que no cabe en un modelo
├── views/          un archivo por vista o viewset
├── access/         solo en users/: políticas de acceso a empleados (§6.4)
├── validators/     validadores de campo reutilizables
├── admin.py
├── apps.py
└── urls.py
```

Las carpetas son paquetes con `__init__.py` que reexporta con `__all__`. Nada de
`models.py` de mil líneas.

Ese reexport tiene una trampa cuando la clase se serializa dentro de una migración: el
nombre reexportado tapa al módulo homónimo, y la migración, que importa por ruta de
módulo, se rompe. Se resuelve de dos formas, y las dos están en uso:

- fijando la ruta serializada — `@deconstructible(path='users.validators.CorporateEmailValidator')`;
- no reexportando la clase, cuando no hay dónde fijar la ruta —
  `BaseManager.deconstruct()` arma la ruta con `self.__module__` y no admite un `path`,
  así que `managers/__init__.py` no publica `UserManager` y quien lo necesita lo importa
  del módulo: `from users.managers.UserManager import UserManager`.

### 7.2 Estilo de código

- **La documentación va en español; los comentarios del código, en inglés.** Es
  deliberado: los `.md` los lee gente de la empresa, el código lo lee quien programa.
- Los imports van agrupados bajo cabeceras de comentario, en este orden:

  ```python
  # external libraries imports
  ...

  # internal application code imports
  ...

  # main code       (o "# main class" si el archivo define una clase)
  ```

- **Comillas simples** en el código propio.
- Type hints en las firmas de vistas y servicios
  (`def get(self, request: Request) -> Response:`).
- `flake8` con `max-line-length = 100`, ignorando `E501, E722, W503`; migraciones
  excluidas.
- **Los comentarios tienen reglas propias: §7.3.** En una línea: por defecto no se
  comenta.

### 7.3 Comentarios

**Por defecto, un bloque de código no lleva comentario.** El código sobrecomentado se lee
peor que el código sin comentar: obliga a leer dos veces lo mismo y envejece mal, porque
nadie actualiza un comentario al cambiar la línea de al lado. Si un fragmento necesita un
párrafo para entenderse, casi siempre lo que hay que arreglar es el fragmento —
renombrar una variable, partir una función— no añadir la explicación.

**Comentarios estructurales.** Son marcadores, no explicaciones, y son la única lista
cerrada de comentarios que se escriben sin justificarse:

```python
# external libraries imports        # agrupan los imports (§7.2)
# internal application code imports
# main code                         # o "# main class" si el archivo define una clase
# fields / # relations / # timestamps    # solo dentro de un modelo
```

En el frontend, el equivalente es `// main code`. Nada más entra en esta lista sin
añadirlo antes a este documento.

**Comentarios en prosa.** Se escribe uno solo si pasa esta prueba: *si lo borro, ¿se
pierde información que no está en el código?* Si la respuesta es no, sobra. Los casos que
sí la pasan:

- Una decisión con una alternativa razonable que se descartó, y por qué:
  `# no version prefix: the frontend is the only client and ships with the backend`.
- Una trampa o un comportamiento contraintuitivo que costaría horas redescubrir:
  `# MSSQL_COLLATION only applies on the first boot, with an empty volume`.
- Una frontera de seguridad, donde hace falta decir qué queda cubierto y qué no:
  `# not the list, not the detail fetched by id, not an export`.
- Algo deliberado que parece un error y que alguien "arreglaría" sin el comentario:
  `# touches no table on purpose: a failure here means the URL or CORS is wrong`.
- Un pendiente, siempre con la referencia a §12: `# PENDING (12, #15): ...`.

Los que **no** la pasan, y por tanto no se escriben:

- Repetir la línea siguiente: `# create the user` sobre `User.objects.create(...)`.
- Describir un campo cuyo nombre y `verbose_name` ya lo dicen.
- Narrar comportamiento estándar de Django, DRF o Vue que está en su documentación.
- Encabezar todos los métodos de una clase por simetría, porque uno sí lo necesitaba.
- Marcar código muerto para "por si acaso": se borra, que para eso está el historial.

**Forma.**

- Va encima del bloque que explica, nunca al final de la línea.
- Una o dos líneas. Si necesita más, la explicación pertenece a este documento y el
  comentario solo la cita.
- Cita la sección entre paréntesis cuando la razón vive acá: `(6.4)`, `(§10.2)`.
- En inglés, como todo comentario de código (§7.2).
- Se actualiza junto al código que explica. Un comentario que miente hace más daño que
  no tener ninguno; si al cambiar una línea el comentario deja de ser cierto, se corrige
  o se borra en el mismo commit.

**Docstrings.** El proyecto no las usa. Un nombre bien elegido y una firma con type hints
dicen lo mismo y no se desactualizan. Si una función necesita una docstring para
entenderse, primero se intenta partirla o renombrarla.

### 7.4 Vistas

- Viewsets de DRF para CRUD; `APIView` solo para endpoints puntuales.
- Permiso por defecto `IsAuthenticated` (está en `REST_FRAMEWORK`). Un `AllowAny`
  explícito solo se justifica si el endpoint no toca ninguna tabla — como
  `CsrfTokenView`, que entrega la cookie CSRF antes de que exista una sesión, o
  `LoginView`, que es justo la petición que llega sin ella.
- Toda vista de `Employee` aplica las filas en `get_queryset()`, las columnas en el
  serializer y la escritura con su permiso (§6.4). No hay excepciones "solo para esta
  pantalla".
- La lógica de negocio va en `services/`, no dentro de la vista. La importación del Excel
  y la exportación de listados son servicios, no vistas.

### 7.5 Pruebas

**No hay suite de pruebas en esta etapa** y no se generan archivos de test. El commit
`043ea35` retiró el andamiaje de `pytest` que se había creado sin usar. No volver a
crearlo sin acordarlo antes.

---

## 8. Convenciones del frontend

### 8.1 Estructura

```
src/
├── app/         App.vue, main.ts, router.ts
├── assets/
├── components/  componentes reutilizables
├── services/    un servicio por dominio de la API
├── shared/      código transversal (services/BaseService.ts)
├── stores/      stores de Pinia
├── types/       interfaces por dominio: <dominio>.types.ts
└── views/       una vista por ruta
```

Import con alias `@/` (mapeado a `src/`), nunca con rutas relativas largas.

### 8.2 Servicios

- **`BaseService` es el único archivo que importa axios.** Ahí viven `baseURL`,
  `withCredentials` y la configuración de CSRF que toda petición necesita.
- Cada servicio es una **clase con miembros estáticos que extiende `BaseService`**, con
  una constante privada `API_URL` y un método por endpoint que devuelve una promesa ya
  tipada. Ver `AuthService.ts`.
- Los tipos de la respuesta se declaran en `types/<dominio>.types.ts`, no dentro del
  servicio.

### 8.3 Componentes y vistas

- `<script setup lang="ts">` siempre. Composition API, nada de Options API.
- Estado local de una vista con `ref`. Pinia solo para estado compartido entre vistas
  (la sesión del usuario, por ejemplo).
- Toda llamada a la API maneja tres estados visibles: cargando, éxito y error, y el error
  se muestra con `getApiErrorMessage()`.
- **El frontend no recorta filas ni columnas.** Pide y muestra lo que llega: el recorte
  ya viene hecho del backend (§6). Un campo que no viene en la respuesta simplemente no
  se dibuja. Si el frontend recortara, habría dos implementaciones de la misma regla y
  una se quedaría vieja.
- **Todo el texto visible va en español**, incluidas las rutas (§4.1). El código
  (variables, funciones, componentes, archivos) en inglés.
- Estilos con clases de Bootstrap. CSS propio solo cuando Bootstrap no alcanza.
- Accesibilidad mínima: `role="alert"` / `role="status"` en los avisos, botones
  deshabilitados mientras carga, tablas con `<th scope>`.
- Ocultar acciones de edición a quien no es Talento Humano es **comodidad de interfaz**,
  no seguridad: el backend niega el método igual (§3.3).

### 8.4 Limpieza pendiente

`src/stores/counter.ts` se borró al aparecer el primer store real (`stores/session.ts`).
Quedan los `.keep` de las carpetas que todavía están vacías; cada uno se borra cuando su
carpeta reciba su primer archivo.

---

## 9. Base de datos y entorno local

- El motor es **SQL Server**; nunca se asume PostgreSQL ni SQLite, ni siquiera en
  desarrollo: el comportamiento de collation, tipos y `LIMIT/OFFSET` difiere.
- La aplicación se conecta con un login propio (`sigth_app`), **nunca con `sa`** (§10.2).
- `TrustServerCertificate=yes` es **solo para local**. En producción, `DB_EXTRA_PARAMS`
  va vacío.
- Migraciones: se generan por app (`makemigrations users employees`) y se revisan antes
  de commitear. En producción las corre TI en su despliegue, no un desarrollador.

**`POR CONFIRMAR`** — Quién administra el esquema (§12 #11). Hoy lo administra Django con
sus migraciones. TI suele trabajar con `managed = False` + `db_table` en `Meta`: las tablas
las crean ellos y Django solo lee y escribe. Pasar a eso después es barato mientras no haya
datos reales en producción; con datos cargados, cualquier cambio de nombres o de tipos
exige migrar los datos.

### 9.1 Guías de montaje

- **`docs/sql-server-local.md`** — montaje en macOS con Apple Silicon (Docker emulado +
  Homebrew). Escrita sobre una máquina real; sigue siendo válida para quien trabaje en Mac.
- **`docs/sql-server-local-windows.md`** — **`POR CONFIRMAR`**, falta escribirla
  (§12 #9). Es el entorno de desarrollo actual.

Si algo de un montaje cambia, se actualiza esa guía en el mismo commit.

---

## 10. Seguridad

### 10.1 Principios

- **Todo lo que cambia entre entornos cuelga de `DEBUG`**, que sale del `.env` y su valor
  por defecto es `False`: un servidor con el `.env` mal puesto se queda en el modo seguro,
  no en el inseguro.
- Menor privilegio en todo: el login de base de datos, los empleados que ve un usuario,
  los orígenes de CORS.
- Ante la duda, no exponer. Un endpoint que devuelve de más no se detecta hasta que ya se
  filtró.

### 10.2 Secretos, credenciales y sesión

- **Ningún secreto en el repositorio.** `SECRET_KEY`, credenciales de base de datos, hosts
  y orígenes salen del `.env` con `python-decouple`. Los `.env.example` llevan las claves
  con el valor vacío y una nota de qué poner.
- **Nunca commitear `.env`** (§11.2).
- Vite **incorpora las variables `VITE_` al bundle como texto plano**: en `frontend/.env`
  nunca va un secreto, solo la URL de la API.
- La base se conecta con `sigth_app`, **nunca con `sa`**. En local ese login es `db_owner`
  de la base `sigth` (Django lo necesita para migrar); en producción se aprieta a
  `db_ddladmin` + `db_datareader` + `db_datawriter`.
- **Sesión por cookie de Django.** Backend y frontend comparten dominio, así que la cookie
  de sesión alcanza: es `httpOnly`, está protegida por CSRF, se revoca del lado del
  servidor y no obliga al frontend a escribir ni guardar tokens. Por eso Axios va con
  `withCredentials: true`, con `xsrfCookieName: 'csrftoken'` /
  `xsrfHeaderName: 'X-CSRFToken'` y con `withXSRFToken: true`: la sesión tiene que
  viajar en cada petición. Ese último desde Axios 1.6, que si no solo manda la cabecera
  CSRF al mismo origen — en producción backend y frontend comparten dominio, pero en
  desarrollo Vite y Django están en puertos distintos y todo POST volvería como 403.
- `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`,
  `SESSION_SAVE_EVERY_REQUEST = True` (la inactividad se mide de verdad).
  `CSRF_COOKIE_HTTPONLY = False` a propósito: el JavaScript tiene que poder leer el token
  para mandarlo en la cabecera.
- Duración de sesión actual: 8 horas (§12 #6).
- **Las contraseñas no se pegan en la línea de comandos**: quedan en el historial del
  shell y en la lista de procesos.

### 10.3 Producción y despliegue

- **TI monta el software en su propio servidor.** Las decisiones de infraestructura
  (sistema operativo, servidor web, proceso de despliegue, quién corre las migraciones)
  son de ellos. El repositorio no asume ninguna y no trae configuración de despliegue
  hasta que TI la defina (§12 #8).
- Con `DEBUG=False` se activan: `SECURE_SSL_REDIRECT`, HSTS a un año con subdominios y
  preload, `SECURE_CONTENT_TYPE_NOSNIFF`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
  `X_FRAME_OPTIONS = 'DENY'` y el renderer JSON puro. **Nada de esto se toca sin motivo.**

---

## 11. Git y repositorio

### 11.1 Ramas

- `main` — versiones estables y lo que se muestra a la empresa. Recibe merges **solo
  desde `develop`**.
- `develop` — integración. Es la base de todo trabajo nuevo.
- `feature/<algo-corto>` — se saca de `develop` y vuelve a `develop`.

Nunca se trabaja directo sobre `main`.

### 11.2 Qué nunca se commitea

`.gitignore` cubre, y esto es deliberado:

- **Secretos**: `.env`, `backend/.env`, `frontend/.env`, `frontend/.env.local`.
- Entornos y artefactos: `backend/.venv/`, `__pycache__/`, `*.py[cod]`, `*.sqlite3`,
  `backend/staticfiles/`, `.pytest_cache/`, `frontend/node_modules/`, `frontend/dist/`.
- **Datos de empleados**: `*.xlsx`, `*.xls`, `*.csv`. El Excel de Talento Humano **no
  entra al repositorio** en ninguna circunstancia, ni siquiera recortado o para probar la
  importación. Si hace falta un archivo de ejemplo, se inventan los datos.
- Archivos de sistema y editor: `.DS_Store`, `.idea/`, `.vscode/`.

Si un secreto o un archivo con datos de personas se commitea por error, no basta con
borrarlo en un commit siguiente: hay que rotar la credencial y avisar.

### 11.3 Mensajes de commit

Conventional commits, en **inglés**, en minúscula, con ámbito cuando aplica:

```
feat(backend): add field access policy skeleton
chore(frontend): mount router view and load bootstrap styles
docs: document local sql server setup on macos
```

Tipos en uso: `feat`, `chore`, `docs`. El cuerpo, cuando existe, explica **por qué** se
hizo así, no qué archivos cambiaron.

Commits pequeños y de un solo tema. Nada de "varios arreglos".

---

## 12. Pendientes

Cada pendiente se cierra con alguien de fuera del código. Al cerrarlo: implementarlo,
quitar el comentario `PENDING` correspondiente y borrar la fila de esta tabla. **Los
números no se corren ni se reutilizan** al cerrar una fila, para que las citas
`(12, #n)` del código y de `docs/` sigan apuntando a lo mismo.

| # | Qué falta | Con quién se cierra | Dónde impacta |
|---|---|---|---|
| 3 | Volumen de empleados, direcciones y usuarios concurrentes | Talento Humano | Paginación (#5), índices, decisiones de rendimiento |
| 5 | Tamaño de página contra el volumen real de empleados | Talento Humano | `REST_FRAMEWORK['PAGE_SIZE']`, hoy 25 |
| 6 | Tiempo de inactividad de la sesión | Seguridad de la Información | `SESSION_COOKIE_AGE`, hoy 8 horas |
| 7 | Collation real de la instancia de producción | TI | Orden y comparación de `ñ` y tildes en búsquedas de apellidos |
| 8 | Servidor de despliegue: versión de SQL Server, sistema operativo y proceso | TI | §10.3, `docs/sql-server-local.md` §2; se asumió SQL Server 2022 |
| 9 | Guía de montaje de SQL Server en Windows | — | `docs/sql-server-local-windows.md` (§9.1) |
| 10 | **Límite de intentos de ingreso fallidos** — hoy el login no tiene ninguno | Seguridad de la Información | `users/views/LoginView.py`, `docs/autenticacion.md` |
| 11 | **Quién administra el esquema de la base**: Django con migraciones, o TI con sus scripts (`managed = False` + `db_table`). Si es TI: qué tablas (¿solo negocio, o también usuarios e historial?), con qué nombres y tipos. Cerrarlo antes del primer despliegue a producción | TI | §9, `Meta` de cada modelo, permiso `db_ddladmin` de `sigth_app` (§10.2) |
| 12 | **Foto del empleado**: dónde se guardan los archivos en producción y cómo se respaldan | TI | Campo de archivo en `Employee` (§5.1) y la dependencia Pillow para validar imágenes |
| 13 | **Formación**: la lista de AROs y formaciones, y qué se registra de cada una | SST | Catálogo de formaciones + tabla empleado–formación (§5.1) |
| 14 | Qué contiene el campo "Prórroga indefinido"; hoy es texto libre | Talento Humano | `Employee.indefinite_extension` |
| 15 | Qué campos del empleado son obligatorios; hoy solo estado, identificación y nombre | Talento Humano | `employees/models/Employee.py` |
| 16 | Listas de ciudades, municipios y nacionalidades; hoy son texto libre | Talento Humano | `Employee.city`, `birth_municipality`, `nationality` |
