# Demostración: cómo probar todas las funcionalidades

Cómo armar una base de demostración y recorrer, cuenta por cuenta, todo lo que hace el
SIGTH. Los datos son **inventados** (nombres, identificaciones, salarios y nombres de los
centros de costos). Nunca se mezclan con datos reales: los comandos solo corren con
`DEBUG=True` y usan un rango de identificaciones reservado (`9000000001`–`9000009999`).

---

## 1. Armar la demo

Con el backend apuntando a la base local y `DEMO_USERS_PASSWORD` definido en
`backend/.env` (al menos 12 caracteres):

```powershell
cd backend; .venv\Scripts\python.exe manage.py migrate
cd backend; .venv\Scripts\python.exe manage.py seed_demo
```

`seed_demo` recrea, en este orden:

1. **Empleados** (`seed_demo_employees --replace`): 78 empleados sobre el organigrama real,
   con fotos generadas, prórrogas, retirados y los casos de la tabla de §3.
2. **Cuentas** (`seed_demo_users --replace`): una por perfil (§2).
3. **Cortes mensuales** (`seed_demo_cuts --replace`): los 12 meses anteriores al actual,
   aproximados con las fechas de ingreso y retiro.

Se puede correr las veces que haga falta: borra lo que creó la vez anterior. Con la misma `--seed` (2026 por
defecto) salen los mismos empleados; las fechas se calculan respecto al día en que se
corre, así que siempre hay ingresos, retiros y vencimientos "de este mes".

---

## 2. Cuentas

Todas con la contraseña de `DEMO_USERS_PASSWORD`. El dominio es el de
`CORPORATE_EMAIL_DOMAIN`.

| Cuenta | Perfil | Qué ve |
|---|---|---|
| `demo.talento@…` | Talento Humano | Todos los empleados y todas las columnas. Es el único que edita. También entra al admin |
| `demo.gerencia@…` | Gerencia General | Todo, en solo lectura |
| `demo.sst@…` | SST - SGI | Todos los empleados, sin contacto, salario y contrato, pensión ni observaciones |
| `demo.director@…` | Director | Solo la Dir. Procesos Técnicos (10 empleados); sin observaciones ni sociodemográfico |
| `demo.lider@…` | Líder | Solo las secciones Calidad y Mantenimiento (8 empleados) |
| `demo.coordinador@…` | Líder | Solo la sección Soldadura (5 empleados) |
| `demo.ti@…` | Sin perfil (TI) | Nada por el frontend; el admin, en solo lectura |

---

## 3. Qué casos trae

Los datos aleatorios dan la variedad general (sexo, edades, categorías, aprendices,
temporales, pacto colectivo). Encima, con fechas fijas respecto al día de hoy:

| Caso | Para probar |
|---|---|
| 2 ingresos este mes y uno o dos en cada uno de los últimos meses | Reporte "Ingresos del mes", indicador de ingresos, evolución |
| 1 retiro este mes y retiros repartidos en el año (11 retirados en total) | Reporte "Retiros del mes", evolución, listado filtrado por Retirado |
| Un contrato vencido hace 6 días, sin prórroga | Vencimientos en rojo, aviso en la ficha |
| Contratos que vencen en 3, 9, 12, 27, 41 y 43 días aprox. | Vencimientos en amarillo, contador de la barra |
| Un contrato fijo de 3 meses sin prórrogas, por vencer | Prórroga sugerida a 3 meses |
| Contratos fijos de 6 meses con 3 o más prórrogas | Prórroga sugerida a 1 año (regla legal) |
| Un contrato fijo especial | Prórroga sin sugerencia: la fecha la digita TH |
| Centros de costos con nombre | Columna "Nombre centro de costos" |
| 12 cortes mensuales; los de 2025 con el salario antes del aumento (9 %) | Selector de mes, evolución, comparativos de salario entre años |

---

## 4. Recorrido

Cada paso dice con qué cuenta hacerlo y qué debería pasar.

### 4.1 Directorio (`/empleados`)

- [ ] **TH** · Listado: buscar por nombre o identificación; filtrar por estado,
  dirección y sección.
- [ ] **TH** · Filtro "Ingreso" desde el primer día del mes actual: salen los 2
  ingresos del mes.
- [ ] **TH** · Filtro "Vencimiento" de hoy a 50 días: salen los contratos por vencer.
- [ ] **TH** · Abrir una ficha, volver con el botón atrás del navegador: los filtros
  siguen puestos (están en la dirección de la página).
- [ ] **SST** · No aparece el filtro "Vencimiento". Si se pone a mano en la dirección
  (`?vence_hasta=…`), el backend lo ignora.
- [ ] **Director** · Solo salen los 10 empleados de Procesos Técnicos. Pedir por la
  dirección `/empleados/<id>` de alguien de otra dirección: "no encontrado".
- [ ] **TH** · Selector de mes: "Corte de <mes pasado>". Sale el aviso "Datos al …" y
  un retirado de ese mes aparece como Retirado. "Rehacer este corte" solo aparece en el
  último corte.
- [ ] **TH** · Pestaña **Organigrama**: "Expandir todo" y "Contraer todo"; el Gerente
  General arriba.
- [ ] **Líder** · Organigrama: solo sus secciones; quien tiene un jefe fuera de ellas
  queda arriba con "Reporta a …".
- [ ] **TH** · Pestaña **Por dirección**: Gerencia y Junta Directiva primero, luego cada
  dirección con sus secciones y conteos.

### 4.2 Ficha y edición (solo TH)

- [ ] Ficha: "Centro de costos" y, debajo, "Nombre centro de costos".
- [ ] Editar un empleado, cambiar el estado a Retirado y guardar sin fecha: "La fecha de
  retiro es obligatoria…". Con una fecha anterior al ingreso: error. Con una fecha
  válida: guarda.
- [ ] Volverlo a Activo: la fecha de retiro desaparece.
- [ ] **Prórrogas**:
  - En la ficha del contrato **vencido**, el bloque Salario y contrato dice "Vencido hace
    6 días".
  - La "Nueva fecha de vencimiento" viene sugerida; "Rige desde" es el día siguiente al
    vencimiento.
  - "Registrar prórroga": el vencimiento cambia y la prórroga aparece en la lista.
  - En el contrato fijo de **3 meses** sin prórrogas, la sugerencia es a 3 meses.
  - En uno de **6 meses** con 3 prórrogas, la sugerencia es a 1 año.
  - En el **fijo especial**, no hay sugerencia.
- [ ] **Gerencia** · La misma ficha no tiene botón de editar ni formulario de prórrogas.

### 4.3 Vencimientos (`/vencimientos`, solo TH)

- [ ] La barra muestra "Vencimientos" con un contador.
- [ ] El vencido va primero y en rojo; el resto, en amarillo, por fecha.
- [ ] Registrar la prórroga del vencido (§4.2) y volver: ya no está.
- [ ] **Gerencia / SST** · No aparece el ítem; `/vencimientos` lleva al directorio.
- [ ] **Correo**, desde la consola:

  ```powershell
  cd backend; .venv\Scripts\python.exe manage.py send_contract_alerts
  cd backend; .venv\Scripts\python.exe manage.py send_contract_alerts
  ```

  La primera vez imprime el correo (sin `EMAIL_HOST` sale por consola); la segunda dice
  que ya se envió hoy. `--force` lo reenvía. El envío queda en Admin → Envíos de
  vencimientos.

### 4.4 Reportes (`/reportes`)

- [ ] **TH** · "Ingresos del mes": salen los ingresos del mes actual, con la columna
  Fecha de ingreso. Cambiar el mes.
- [ ] **TH** · "Retiros del mes": el retiro de este mes; cambiar a un mes anterior.
- [ ] **TH** · "Empleados por dirección": pide elegir la dirección.
- [ ] **TH** · "Personal por líder": buscar "Cardona Sierra" (Jefe Planta) y elegirlo:
  sale todo su equipo hacia abajo, con la columna Jefe inmediato.
- [ ] **TH** · Campos: agregar Salario actual y Nombre centro de costos; subir y bajar el
  orden.
- [ ] **TH** · Descargar en **Excel**, **CSV** y **PDF**. Los tres traen las mismas filas
  y columnas que la vista previa. El PDF va horizontal, con logo, filtros y número de
  página.
- [ ] **SST** · En Campos no aparecen Salario, Contrato ni Observaciones; los filtros
  de contrato y vencimiento tampoco.
- [ ] **Director** · Cualquier reporte trae solo su dirección.
- [ ] **TH** · Desde el listado con filtros puestos, "Exportar" abre Reportes con esos
  mismos filtros.

### 4.5 Analítica (`/analitica`)

- [ ] **TH** · Resumen: activos de hoy, 2 ingresos y 1 retiro del mes, y la variación
  frente al mes anterior.
- [ ] **TH** · Evolución: 13 puntos (12 cortes y hoy), con cambios mes a mes.
- [ ] **TH** · Periodo "Corte de diciembre de 2025": la tabla de salario por sección
  muestra salarios menores que los de hoy (antes del aumento).
- [ ] **TH** · "Comparar con" otro mes: cambia la tabla de variación por dirección.
- [ ] **TH** · Filtro Sexo = Femenino, o Categoría: todos los indicadores se recalculan.
- [ ] **TH** · Vinculación por sexo: los aprendices van en su propia fila.
- [ ] **TH** · "Ver tabla" en una gráfica; "PNG" la descarga como imagen; "Descargar
  Excel" baja todos los indicadores, una hoja por indicador con su nombre en español.
- [ ] **SST** · No aparecen "Tipo de contratación por sexo" ni "Personal y salario por
  sección".
- [ ] **Director / Líder** · Todo se calcula solo sobre su alcance.
- [ ] **TI** · "Tu perfil no tiene indicadores para mostrar."

### 4.6 Admin (`/admin/`)

- [ ] **TH** · Centros de costos: cambiar un nombre; se ve en la ficha.
- [ ] **TH** · En un empleado, las prórrogas se ven pero no se pueden agregar ni editar
  (se registran desde la ficha).
- [ ] **TI** · Entra y ve empleados, cortes mensuales y envíos de
  vencimientos, todo en solo lectura.

### 4.7 Corte mensual programado

```powershell
cd backend; .venv\Scripts\python.exe manage.py take_monthly_cut
```

Fuera del día 1 no hace nada. Con `--date <último día del mes pasado>` dice que ese corte
ya existe (lo armó la demo) y no lo repite. Para verlo tomar uno, se borra ese corte
desde la consola de Django o se vuelve a armar la demo con un mes menos
(`seed_demo_cuts --replace --months 11`).

### 4.8 En el celular

- [ ] Con la ventana angosta, la barra superior se pliega en un botón de menú.
