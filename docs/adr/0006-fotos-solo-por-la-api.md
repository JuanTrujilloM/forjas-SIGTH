# 0006. Fotos de empleados servidas solo por la API

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada (ubicación en producción pendiente, §12 #12 de `CLAUDE.md`)

## Contexto

La foto de un empleado es un dato personal. Un archivo servido directamente por el
servidor web lo puede ver cualquiera que tenga el enlace, sin pasar por el control de
acceso.

## Decisión

- Las fotos se guardan en `MEDIA_ROOT`, con nombre aleatorio.
- **No hay ruta pública `/media/`**. La foto sale por `GET /api/employees/{id}/photo/`,
  con el mismo recorte de acceso que el resto.
- Se genera una miniatura de 80×100 para el listado.
- Solo se aceptan JPG, PNG o WebP de hasta 5 MB, verificados con Pillow.

## Consecuencias

- La foto queda protegida igual que cualquier otro dato.
- Servir imágenes por Django es más costoso que por un servidor web. Es aceptable para el
  volumen interno esperado.
- Los archivos anteriores no se borran al cambiar la foto, porque el historial los
  referencia. Crecerán hasta que exista una regla de retención.
- TI debe definir dónde vive `MEDIA_ROOT` en producción y cómo se respalda.
