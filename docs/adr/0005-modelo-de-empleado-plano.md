# 0005. Un modelo de empleado plano, espejo de la especificación de TH

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada

## Contexto

La fuente de los datos es la especificación "Base de Datos Personal" de Talento Humano:
una lista de campos, con su tipo, sus valores y quién los ve. Esa especificación reemplaza
las columnas del Excel actual.

## Decisión

`Employee` es **un solo modelo con una columna por dato**, agrupadas en los bloques que
usa el control de acceso. Solo se modelan como tablas aparte lo que es catálogo editable
(`Position`) o lo que se repite (`ContractExtension`). Edad, antigüedad y valor hora
**se calculan**, no se guardan.

## Consecuencias

- La correspondencia con la especificación y con el Excel es directa, lo que facilita
  validar con Talento Humano y construir la importación.
- Los datos calculados no se desactualizan, que era un problema del Excel.
- El modelo es ancho. Agregar un campo exige decidir en qué bloque de acceso va: si no
  está en ningún bloque, nadie lo ve.
- Del cargo anterior se guarda solo el último, sin historial de cargos.
