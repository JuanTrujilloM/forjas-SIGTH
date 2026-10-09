# 0008. Reportes descargables con el mismo recorte de acceso

**Fecha:** 2026-10-07
**Estado:** Aceptada

## Contexto

Talento Humano pidió un módulo de reportes: consultar por pantalla y descargar en Excel,
CSV o PDF, con filtros combinados y elección de campos, además de reportes listos
(ingresos y retiros del mes, por dirección, por líder, por sección). Un archivo
descargado es una copia de datos personales que sale del sistema: si el reporte trajera
una fila o una columna de más, la fuga ya no se puede deshacer.

## Decisión

- **Un solo camino para los datos.** La vista previa (`GET /api/employees/report/`) y la
  descarga (`GET /api/employees/export/`) son acciones del mismo `EmployeeViewSet`:
  heredan su `get_queryset()` (filas por perfil), sus filtros, su búsqueda y su orden. No
  hay un queryset aparte para exportar.
- **Las columnas salen de la misma matriz por perfil.** El usuario elige campos solo
  entre los que su perfil ve; un campo pedido que no ve se ignora, igual que un filtro.
  El catálogo de columnas exportables vive en `EmployeeExportService` y cada columna debe
  estar en un bloque de `EMPLOYEE_FIELD_GROUPS`, o no la ve nadie.
- **Cada descarga queda registrada** en `EmployeeExportLog`: usuario, fecha, formato,
  título, filtros, campos y número de filas. Se consulta en el admin, en solo lectura.
- **Formatos**: Excel con `openpyxl` (ya estaba en las dependencias), CSV con la librería
  estándar (punto y coma y BOM, para que Excel en español lo abra bien) y PDF con
  **`reportlab`**.
- Los textos que empiezan por `=`, `+`, `-`, `@` se escapan al escribir Excel y CSV, para
  que una hoja de cálculo no los ejecute como fórmulas.

## Alternativas descartadas

- **Generar el archivo en el frontend.** Habría dos implementaciones del recorte, y el
  frontend nunca es la frontera de seguridad.
- **WeasyPrint para el PDF.** Arma el PDF desde HTML, pero necesita librerías del sistema
  (Pango, Cairo) en el servidor de TI. `reportlab` está escrito en Python y solo depende
  de Pillow, que ya estaba en el proyecto.

## Consecuencias

- Un archivo descargado nunca trae más de lo que el usuario ve en pantalla.
- El PDF de un reporte con muchas columnas reduce la letra para que quepan en una hoja
  horizontal. Para trabajar con muchas columnas, el formato indicado es Excel.
- El registro de descargas crece con el uso. Su retención va con la del historial.
