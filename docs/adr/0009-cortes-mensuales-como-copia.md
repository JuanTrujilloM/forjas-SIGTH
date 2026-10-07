# 0009. Cortes mensuales como copia de los empleados

**Fecha:** 2026-10-07
**Estado:** Aceptada (la carga de los meses anteriores al primer corte la define TI)

## Contexto

El Excel de Talento Humano lleva una hoja por mes, y la gente consulta cómo estaban los
empleados en un mes dado. La analítica pide la evolución mensual y anual de los
colaboradores y comparar meses y años **conservando las fechas de corte**: un mes ya
reportado no puede cambiar porque después se corrija un dato. El SIGTH solo guardaba el
estado actual.

## Decisión

- **Un corte por mes es una copia**, no algo que se deduce del historial. `MonthlyCut`
  guarda la fecha de corte (último día del mes) y `EmployeeSnapshot`, por cada empleado
  de ese mes, una copia de **todas** sus columnas en un campo JSON, calculadas a esa
  fecha (edad, antigüedad, valor hora).
- Entran los empleados activos al cierre y los que se retiraron durante ese mes.
- La dirección, la sección, el estado, el nombre y la identificación de ese mes se
  guardan también como columnas reales, porque con ellas se recortan las filas por perfil
  y se filtra y busca. Un director ve a quienes estaban en su dirección **ese mes**.
- **Las columnas se recortan al leer** con la misma matriz por perfil
  (`EmployeeFieldPolicy.trim`), así una copia sirve para todos los perfiles.
- El corte lo toma `manage.py take_monthly_cut` el día 1, en la misma tarea diaria del
  aviso de vencimientos. Un mes cerrado no cambia. Solo Talento Humano puede rehacer el
  **último** corte, por si había un error que se corrigió justo después del cierre.

## Alternativas descartadas

- **Derivarlo del historial de `django-simple-history`.** Una corrección retroactiva
  cambiaría los números de un mes ya reportado, la regla de retención del historial
  podría borrar meses que se consultan, y la fecha en que se editó un registro no es la
  fecha del hecho.
- **Una tabla con una columna por campo, espejo de `Employee`.** Cada columna nueva del
  empleado exigiría tocar también los cortes. Con unos 230 empleados por mes, agregar en
  Python sobre el JSON es inmediato.

## Consecuencias

- Los meses anteriores al primer corte no existen en el sistema. Si se quieren, los
  carga TI. En desarrollo, `seed_demo_cuts` arma doce meses aproximados.
- Los cortes crecen unas 230 filas por mes. No se borran.
- Si TI termina administrando el esquema (`managed = False`), el campo JSON necesita SQL
  Server 2016 o posterior.
