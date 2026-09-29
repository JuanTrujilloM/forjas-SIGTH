# 0001. Backend en Django + DRF sobre SQL Server

**Fecha:** registrada el 2026-09-29; la decisión se tomó durante el desarrollo (desde el 2026-08-25)
**Estado:** Aceptada

## Contexto

SIGTH necesita:
- una API con autenticación;
- un control de acceso fino;
- historial de cambios;
- un panel de administración para que TI gestione cuentas.

La empresa ya opera **SQL Server** y TI mantendrá el sistema en su propia infraestructura.

## Decisión

El backend se construye con **Django 5.2 LTS** y **Django REST Framework**, conectado a
**SQL Server** con `mssql-django` y `pyodbc` (ODBC Driver 18). En desarrollo también se
usa SQL Server, en un contenedor, nunca SQLite ni PostgreSQL.

## Consecuencias

- El admin, la autenticación, el ORM y las migraciones vienen de fábrica. El admin es la
  herramienta de TI.
- Django 5.2 es LTS, así que tiene soporte largo.
- Se usa el motor que TI ya conoce y respalda.
- `mssql-django` es menos usado que los *backends* nativos de Django. Hay trampas conocidas
  (p. ej. `dbshell` no funciona contra el contenedor local), documentadas en las guías de
  `docs/`.
- Desarrollar contra SQL Server exige Docker y el driver ODBC en cada máquina.
