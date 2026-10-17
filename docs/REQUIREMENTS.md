# Requisitos

> Solo se registran requisitos con fuente explícita. Todo lo demás queda en "Por definir".

## Contexto

- Proyecto: Centro de coordinación agéntico para la crisis del agua en Panamá Oeste.
- Hackathon FISC, equipo 04, Reto 1 (Agua). Fuente: `README.md`.

## Requisitos de entrega (fuente: plantilla `README.md`)

- Describir el problema: qué resuelve, para quién y con qué datos.
- Documentar la arquitectura de agentes: agentes, herramientas, flujos y **punto de intervención humana**, con diagrama.
- Listar tecnologías y fuentes de datos.
- Instrucciones de instalación y ejecución, con credenciales de demo sin claves reales (`.env.example`).
- **Evals: al menos 15 casos de prueba**, con métrica y resultados.
- Bitácora de IA: qué se hizo con IA, con qué herramienta y qué se modificó a mano.
- Entrega: tag de git `final-24h` sobre el último commit válido al cumplirse la hora 24.

## Restricciones (fuente: instrucciones del equipo)

- No usar datos reales de ciudadanos ni información personal; solo datos sintéticos o públicos.
- No incluir credenciales reales en el repositorio.
- No conectar proveedores de modelos, bases de datos externas, mapas, mensajería ni notificaciones sin aprobación.
- Sin despliegues, pagos ni cambios remotos en GitHub sin autorización.

## Requisitos funcionales

La fuente de verdad es [AGENT_CRITERIA_AND_DECISION_RULES.md](AGENT_CRITERIA_AND_DECISION_RULES.md) (rev.4), que define los seis agentes, sus reglas `[CONF]`, `[PROV]`, `[PEND]` y `[PROP]`, y los criterios de aceptación de cada uno (apartado I). Las decisiones de la usuaria del 2026-10-17 que todavía no están en ese documento figuran en [DECISIONS.md](DECISIONS.md) (DEC-C01 a DEC-C16).

Requisitos de la etapa 1 (instrucción de implementación, 2026-10-17):

- Flujo: reporte simulado → A1 → A2 → A3 → A4 → propuesta de plan → aprobación simulada → registro de trazabilidad.
- Modelos de datos validados, identificadores únicos, separación entre lógica determinista y modelos de IA.
- Registro de originales, datos normalizados, cálculos, incertidumbres, decisiones y versión de reglas.
- Los datos desconocidos se conservan como desconocidos; no se inventan valores.
- `T = min(100, días_sin_agua / 5 × 100)`. Desde DEC-C15, el tiempo sin agua también compensa la demanda con el 50 %.
- Proveedor y modelo de IA configurables por entorno, sin claves en el código.
- Interfaz simulada de WhatsApp e interfaz de aprobación que funcionen sin servicios externos.
- Integraciones intercambiables (mapas, geocodificación, rutas, IA, mensajería, transcripción, base de datos, archivos, monitoreo) que funcionen sin credenciales y muestren `NOT_CONFIGURED` cuando falten.

## Requisitos no funcionales

- Debe ejecutarse en Windows nativo con `uv`.
- Pruebas automatizadas sin credenciales ni Internet; pruebas de integración que se activan por separado.
- Las claves y tokens nunca aparecen en el repositorio, los logs ni los mensajes de error.
- No se envían teléfonos ni datos personales a servicios que no los necesitan.
- Ningún despacho real, mensaje externo ni servicio de pago sin aprobación explícita.
