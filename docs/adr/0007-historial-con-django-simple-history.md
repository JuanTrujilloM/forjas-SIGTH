# 0007. Historial de cambios con django-simple-history

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada (retención pendiente)

## Contexto

Con el Excel no se puede saber quién cambió un dato ni cuándo. Ante un reclamo sobre un
dato de una persona, o sobre quién le dio acceso a alguien, hay que poder responder.

## Decisión

Se usa `django-simple-history` en `Employee`, `ContractExtension`, `User` (sin
contraseña ni último ingreso) y `UserSection`. El `HistoryRequestMiddleware` registra
qué usuario hizo cada cambio. El historial se consulta desde el admin.

## Consecuencias

- Queda trazabilidad completa de los datos de personas y de los accesos.
- Las tablas de historial crecen con cada cambio. Hay que definir cuánto tiempo se
  retienen.
- Los cambios hechos por fuera de Django, directo en la base, no quedan registrados.
