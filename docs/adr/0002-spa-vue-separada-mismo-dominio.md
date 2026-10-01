# 0002. Frontend SPA en Vue 3, separado del backend y servido en el mismo dominio

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada

## Contexto

Las pantallas de negocio (lista, ficha y formulario de empleados) necesitan una interfaz
ágil. El backend debe concentrar la lógica y la seguridad.

## Decisión

El frontend es una **SPA en Vue 3 + TypeScript** (Vite, Pinia, Vue Router, Axios,
Bootstrap), en `frontend/` dentro del mismo repositorio. Solo consume la API bajo
`/api/`. El backend no renderiza pantallas de negocio: solo el admin. En producción,
frontend y backend se sirven **bajo el mismo dominio**. La API no lleva prefijo de
versión porque su único cliente se despliega junto con ella.

## Consecuencias

- La interfaz y la API evolucionan por separado, cada una con sus herramientas.
- El mismo dominio permite usar la cookie de sesión de Django sin tokens (ADR 0003).
- Hay dos procesos de construcción: el de Python y el de Node.
- El frontend nunca es la frontera de seguridad: todo lo que oculta, el backend lo vuelve
  a negar (ADR 0004).
