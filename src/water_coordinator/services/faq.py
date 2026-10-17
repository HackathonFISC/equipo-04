"""Preguntas frecuentes del panel del supervisor. Contenido fijo, redactado a partir de las reglas documentadas."""

FAQ = [
    {
        "pregunta": "¿Qué significa que un plan esté «pendiente de aprobación»?",
        "respuesta": "Lo propuso el sistema a partir de reglas y datos registrados. No es un compromiso de entrega: "
                     "ningún plan se ejecuta sin la aprobación del supervisor (DEC-18).",
    },
    {
        "pregunta": "¿Los mensajes propuestos se envían a los ciudadanos?",
        "respuesta": "No. En el prototipo los mensajes del Agente 6 son simulados: se guardan y se muestran aquí, "
                     "pero no salen del sistema. WhatsApp no está conectado.",
    },
    {
        "pregunta": "¿«Aprobado» significa que la cisterna ya salió?",
        "respuesta": "No. Aprobado indica una decisión registrada del supervisor, no una entrega ejecutada. "
                     "Ejecutado y verificado son estados distintos que solo registra el responsable operativo.",
    },
    {
        "pregunta": "¿Las aprobaciones de este panel son reales?",
        "respuesta": "No. Mientras no exista autenticación del supervisor, la API registra todas las decisiones como "
                     "simuladas de prueba. Las decisiones reales solo pueden registrarse por la línea de comandos.",
    },
    {
        "pregunta": "¿Por qué no aparece una hora de llegada?",
        "respuesta": "Porque no hay una hora confirmada en los registros y el sistema no la estima por su cuenta.",
    },
    {
        "pregunta": "¿Qué es una cobertura parcial?",
        "respuesta": "Un plan que cubre entre el 80 % y menos del 100 % de la demanda estimada. Requiere aprobación "
                     "y el Agente 6 prepara un mensaje especial con el volumen previsto y el pendiente.",
    },
    {
        "pregunta": "¿Qué pasa si un plan cubre menos del 80 %?",
        "respuesta": "No se presenta como plan ordinario: requiere una decisión extraordinaria del supervisor con "
                     "justificación registrada.",
    },
    {
        "pregunta": "¿Cómo se decide el orden de atención?",
        "respuesta": "Primero la jerarquía: hospitales, policlínicas, centros de salud, escuelas y después el resto. "
                     "Para el resto se usa P = 0,50·T + 0,25·V + 0,25·A. Si falta un factor, P queda incompleto y se "
                     "pide revisión humana; nunca se toma como cero.",
    },
    {
        "pregunta": "¿El agua de las cisternas está certificada como potable?",
        "respuesta": "No. Para calcular la demanda se asume agua de cisterna limpia, pero eso no es una certificación: "
                     "la fuente y la potabilidad deben validarlas las autoridades competentes.",
    },
    {
        "pregunta": "¿Por qué los planes aparecen incompletos?",
        "respuesta": "Falta la ruta: el Agente 5 aún no está integrado en el flujo y la ubicación de la organización "
                     "está pendiente. Por eso un plan incompleto solo admite aprobación simulada.",
    },
]
