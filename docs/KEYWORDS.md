# Palabras clave para filtrar y clasificar reportes (Agente 1)

> Fuente de código: `src/water_coordinator/services/clasificacion.py`. La prueba `tests/test_ingesta.py::test_keywords_md_y_codigo_coinciden` falla si este documento y el código dejan de coincidir. Si agregas una palabra, agrégala en los dos sitios.

## Cómo se usan

1. Se normaliza el texto: minúsculas, sin tildes y sin espacios repetidos. Por eso `tubería rota` y `tuberia rota` cuentan igual.
2. **Filtro de relevancia:** un reporte es del dominio si contiene algún hashtag o expresión de esta lista. Los reportes no relevantes **no se descartan**. Se conservan como `indeterminado` y quedan *pendientes de información*.
3. **Clasificación:** cada coincidencia suma evidencia para un tipo.
   - Si aparecen a la vez *tubería rota* y *falta de agua*, el tipo es **tubería rota** (la causa) y la falta de agua se registra como consecuencia (A1-R2).
   - Cualquier otra combinación de tipos queda `indeterminado` y va a revisión humana.
4. **Escala de confianza:**

| Nivel | Criterio |
| --- | --- |
| `alta` | Hashtag del tipo, o 2 o más expresiones distintas del mismo tipo, sin conflicto. |
| `media` | Una sola expresión del tipo. |
| `baja` | El modelo de IA, si está configurado, sugiere otro tipo. El registro pasa a revisión. |
| `ninguna` | Tipo indeterminado. |

## Hashtags (texto escrito)

| Hashtag | Tipo | Origen |
| --- | --- | --- |
| `#sinagua` | falta de agua | Pedido por el equipo |
| `#faltadeagua` | falta de agua | Pedido por el equipo |
| `#tuberiarota` | tubería rota | Pedido por el equipo |
| `#idaan` | relevancia (no fija tipo) | Pedido por el equipo |
| `#nohayagua` | falta de agua | Recomendado |
| `#fugadeagua` | tubería rota | Recomendado |
| `#aguacontaminada` | agua contaminada | Recomendado |
| `#aguasucia` | agua contaminada | Recomendado |
| `#panamaoeste` | relevancia | Recomendado |
| `#cisterna` | relevancia | Recomendado |
| `#carrotanque` | relevancia | Recomendado |

`#idaan` marca el reporte como relevante, pero no indica si falta agua, si hay una tubería rota o si el agua está contaminada.

## Expresiones (texto escrito y voz transcrita)

Las transcripciones de audio no traen el símbolo `#`. Por eso se incluyen las formas habladas ("hashtag sin agua", "numeral sin agua") y la forma oral de IDAAN.

### Falta de agua

`sin agua`, `falta de agua`, `no hay agua`, `no llega el agua`, `no ha llegado el agua`, `no sale agua`, `no cae agua`, `se fue el agua`, `corte de agua`, `sin servicio de agua`, `estamos secos`, `la pluma no tiene agua`, `hashtag sin agua`, `numeral sin agua`

### Tubería rota

`tuberia rota`, `tubo roto`, `se rompio la tuberia`, `se rompio el tubo`, `fuga de agua`, `botando agua`, `esta botando agua`, `tuberia danada`, `rotura de tuberia`, `derrame de agua`, `hashtag tuberia rota`, `numeral tuberia rota`

### Agua contaminada

`agua contaminada`, `agua sucia`, `agua turbia`, `agua amarilla`, `agua color cafe`, `agua marron`, `agua con mal olor`, `el agua huele mal`, `agua con olor`, `agua con sabor raro`, `agua con lodo`, `hashtag agua contaminada`

### Relevancia por voz (no fijan tipo)

`idaan`, `i de a a ene`, `idan` (transcripción frecuente de "IDAAN"), `carro cisterna`, `carro tanque`

## Recomendaciones aplicadas

- **Regionalismos de Panamá:** "pluma" se usa para el grifo, "botando agua" para una fuga y "carro cisterna" o "carro tanque" para la cisterna.
- **Errores típicos de transcripción:** "idan" en lugar de "IDAAN", y "hashtag" o "numeral" dichos en voz alta.
- **Señales de calidad del agua:** "turbia", "amarilla", "con lodo", "huele mal". Activan la alerta sanitaria, pero **no** certifican contaminación (A1-R7).
- **No se incluyeron** términos de salud como "diarrea". Son consecuencias posibles, no tipos de afectación, y podrían generar alertas sanitarias falsas.

## Otros datos que extrae el Agente 1 del texto

- **Fecha del incidente:** `hace N días/horas/semanas`, `ayer`, `anoche`, `antier`, `hoy`, `esta mañana`, `desde el lunes`…, `15/10`, `14 de octubre`. Si no aparece, la fecha queda nula y nunca se reemplaza por la fecha de recepción.
- **Unidades afectadas:** `N casas` o `N viviendas`; se cuentan como rurales si el texto dice "rural". También `N edificios`, `N estudiantes` o `N alumnos`, y `N personas`.
- **Instalaciones:**
  - `hospital`, `policlínica`, `centro de salud`, `subcentro de salud`.
  - `escuela`, `colegio`, `centro educativo`.
  - `clínica` se marca como categoría **incierta** (A3-R3).
- **Vulnerabilidad:**
  - Rural, residencial, barriada, urbanización.
  - Comunidad antigua.
  - Niños, bebés, jóvenes o estudiantes.
