# 0004. Control de acceso por perfil, con filas y columnas decididas en el backend

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada. Reemplaza el diseño anterior con matriz de campos por dirección.

## Contexto

El objetivo del sistema es que cada persona vea lo que le corresponde **sin abrir la
información de más**. La especificación de Talento Humano (septiembre de 2026) define
qué empleados ve cada rol y qué bloques de datos ve de ellos. Un diseño anterior, con una
matriz de campos por dirección, se retiró.

## Decisión

- Cada cuenta tiene **un solo perfil**: Talento Humano, Gerencia General, SST - SGI,
  Director, Líder, o sin perfil (TI).
- El perfil decide dos ejes, cada uno en **un único punto** del backend:
  - **filas**: `EmployeeScopePolicy`, aplicada en `get_queryset()`;
  - **columnas**: `EmployeeFieldPolicy`, aplicada en el serializer, los filtros, el
    orden y la búsqueda.
- Un empleado fuera de alcance responde **404**, no 403.
- Solo Talento Humano escribe.

Detalle: [documentación técnica §7.1](../DOCUMENTACION-TECNICA.md#71-perfiles-de-acceso) y el
código de `backend/users/access/`.

## Consecuencias

- Un dato que el perfil no ve no sale por ninguna ruta, ni se puede deducir filtrando.
- El frontend no duplica la regla: muestra lo que llega.
- Cada vista o serializer nuevo debe heredar los *mixins* de acceso. Olvidarlo abre los
  datos, y no hay pruebas automatizadas que lo detecten.
- Un usuario con dos roles (p. ej. el Líder de SST) queda con uno solo y puede ver menos
  de lo que su cargo sugiere.
