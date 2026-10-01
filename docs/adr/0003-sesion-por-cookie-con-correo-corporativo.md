# 0003. Autenticación por sesión de Django con correo corporativo, sin SSO ni tokens

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada

## Contexto

Solo deben entrar personas de la empresa autorizadas por TI. Se evaluó si usar el SSO
corporativo o contraseñas propias, y si guardar tokens en el navegador.

## Decisión

- El ingreso es con **correo corporativo y contraseña**.
- El identificador es el `email` (se eliminó `username`), validado contra
  `CORPORATE_EMAIL_DOMAIN`.
- La sesión es la **cookie de Django**: `httpOnly`, protegida por CSRF y revocable desde
  el servidor.
- Las cuentas las crea TI. No hay auto-registro ni recuperación pública de contraseña.

Detalle: [`docs/guias/autenticacion.md`](../guias/autenticacion.md).

## Consecuencias

- El frontend no guarda ni escribe tokens, así que no hay dónde robarlos con JavaScript.
- Desactivar una cuenta o cerrar su sesión tiene efecto inmediato.
- TI administra las contraseñas: no hay recuperación automática.
- No hay límite de intentos fallidos ni segundo factor (pendiente 6 de la
  [documentación técnica](../DOCUMENTACION-TECNICA.md#12-riesgos-deuda-técnica-y-pendientes)).
- Si más adelante se adopta el SSO de la empresa, habrá que reemplazar el ingreso.
