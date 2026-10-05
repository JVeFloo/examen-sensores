# Informe — Fundamentos de Big Data aplicados al proyecto

**Autores:** Jeshua Vera Flores · Betel Zurisadai Hernández Sánchez
**IDIA 224 — Universidad Politécnica de Querétaro**

---

## 5. Las 5 V aplicadas al proyecto

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o futura ampliación? |
|---|-------------------------------------|------------------|----------------------------------|
| **Volumen** | Cada sensor genera una lectura por minuto; al multiplicarse por miles de sensores y meses de operación, el volumen de datos crece rápidamente y deja de caber en una sola máquina. | Hoy tenemos 100,000 filas (≈ 4.4 MiB). Si el sistema crece a 5,000 sensores midiendo cada segundo, serían 432 millones de filas por día. | Las 100,000 filas están en el **CSV actual**; el escalamiento a 5,000 sensores/segundo pertenece a la **futura ampliación**. |
| **Velocidad** | Los datos llegan de forma continua. La velocidad define cuán rápido podemos reaccionar ante una lectura peligrosa (ej. temperatura > 85 °C). | Hoy una lectura por minuto es suficiente para análisis diferido. La ampliación planea mediciones cada segundo, lo que exige procesamiento en tiempo real. | El ritmo de 1/min aparece en el **CSV actual**; el ritmo de 1/s corresponde a la **futura ampliación**. |
| **Variedad** | Los datos no vienen solo en tablas: también habrá imágenes de las máquinas y texto libre de los reportes de mantenimiento. Cada tipo requiere técnicas distintas de almacenamiento y análisis. | CSV con mediciones (estructurado), fotografía de un rodamiento desgastado (no estructurado), reporte escrito del técnico (no estructurado). | El CSV está en el **CSV actual**; fotografías y reportes están en la **futura ampliación**. |
| **Veracidad** | No todas las lecturas son confiables: sensores descalibrados, picos espurios o datos faltantes pueden generar falsas alertas. Hay que medir y mejorar la calidad. | La lectura máxima de 104.99 °C aparece en 4 registros distintos: podría ser un pico real o un error de calibración del sensor. Hay que validarlo contra el reporte físico. | Está presente en el **CSV actual** (los datos son simulados pero el fenómeno aplica igual). |
| **Valor** | El dato por sí mismo no sirve; sirve cuando permite tomar decisiones que reducen costos o evitan fallas. El valor aquí es prevenir paros de línea y accidentes. | Identificar que **Planta_3** acumula 1,777 alertas de temperatura permite priorizar el mantenimiento de esa planta antes de que falle una máquina. | El hallazgo nace del **CSV actual**; su conversión en acciones preventivas sostenidas es parte de la **futura ampliación**. |

---

## 6. Tipos de datos y procesamiento tradicional

### Clasificación

| Elemento | Tipo | Justificación |
|----------|------|---------------|
| CSV de sensores | **Estructurado** | Tiene un esquema fijo: columnas definidas con tipos de dato consistentes. |
| Mensaje JSON de un sensor | **Semiestructurado** | Tiene estructura (claves y valores) pero el esquema puede variar entre mensajes y admite anidamiento. |
| Fotografía de una máquina | **No estructurado** | Es un conjunto de píxeles sin esquema tabular; para extraer información se necesita visión por computadora. |
| Texto libre de un reporte de mantenimiento | **No estructurado** | Lenguaje natural sin formato predefinido; requiere NLP para extraer entidades, fechas y causas. |

### ¿Por qué 100,000 registros no es Big Data automáticamente?

Big Data no se define solo por el número de filas, sino por **superar
simultáneamente** varias de las 5 V hasta que las herramientas tradicionales
dejan de alcanzar.

Nuestro CSV tiene 100,000 filas y **4.4 MiB**: cabe entero en la memoria RAM
de cualquier laptop moderna y pandas lo procesa en menos de un segundo.
No hay velocidad (es un archivo estático), no hay variedad (solo tabla
numérica) y no hay un problema de distribución. Por eso Python + pandas
en una sola máquina es más que suficiente.

### Limitaciones al aumentar la escala

Si el sistema crece a miles de sensores midiendo cada segundo:

- **RAM insuficiente:** 432 millones de filas por día no caben en memoria.
- **Un solo CPU:** procesar lineal se vuelve inaceptable; se necesita paralelismo distribuido (Spark, Dask).
- **Almacenamiento:** un CSV único deja de servir; hay que pasar a formatos columnares (Parquet) y data lakes.
- **Tiempo real:** un batch nocturno no sirve si la alerta debe emitirse en segundos; se requiere streaming (Kafka, Flink).
- **Variedad:** sumar fotografías y texto libre obliga a herramientas distintas (object storage, pipelines de ML).

---

## 7. Batch y Streaming

### Tipo de procesamiento usado en este proyecto

El programa `analisis.py` realiza **procesamiento por lotes (batch)**.
Lee un archivo que ya está completo en disco, procesa todos los registros
de una sola pasada y produce resultados agregados. No reacciona en tiempo
real a nuevas mediciones.

**Justificación:** el dato ya está acumulado (el CSV es estático), no hay
una fuente que esté empujando mediciones ahora mismo, y el objetivo del
análisis es obtener un panorama histórico, no una alarma inmediata.

### Para emitir una alerta pocos segundos después de recibir una lectura > 85 °C

Usaría **procesamiento en streaming**. Cada lectura entrante se evalúa
en el momento con una regla simple (`temperatura_c > 85`) y, si se cumple,
se dispara un evento de alerta (notificación al operador, registro en
tablero en vivo). Herramientas típicas: Apache Kafka para el transporte
de eventos y Apache Flink o Spark Structured Streaming para el procesamiento.

El tiempo que se exige al resultado es de **segundos**, por lo que no se
puede esperar al batch nocturno.

### Para generar un resumen al terminar el día

Usaría **procesamiento batch**. Al final del día se corre un job que lee
todas las lecturas del día (por ejemplo desde el data lake), calcula
agregados (promedio por planta, cantidad de alertas, máximos) y guarda
el reporte.

El tiempo que se exige al resultado es de **minutos u horas** y el objetivo
es completitud y precisión, no inmediatez, por eso el batch es ideal.

### Relación con el tiempo necesario

| Resultado | Tiempo esperado | Enfoque |
|-----------|-----------------|---------|
| Alerta de temperatura peligrosa | Segundos | Streaming |
| Resumen diario de la planta | Minutos / horas | Batch |
| Análisis histórico de este examen | No urgente | Batch (lo que ya hicimos) |

---

## 8. Lambda y Kappa

### Escenario A — recalcular historial por lotes + procesar mediciones recientes rápidamente

**Elijo arquitectura Lambda.**

Lambda combina dos rutas paralelas: una capa **batch** que recalcula todo
el historial periódicamente (garantiza precisión y completitud) y una
capa **speed** que procesa las mediciones nuevas en streaming (garantiza
baja latencia). Una capa de servicio combina ambos resultados para
responder consultas.

Es exactamente lo que pide el escenario: dos rutas distintas optimizadas
para objetivos distintos.

```
                 ┌─────────────────────────┐
                 │       Sensores          │
                 └───────────┬─────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌──────────────────┐          ┌──────────────────┐
    │   Capa Batch     │          │   Capa Speed     │
    │  (recalcula      │          │ (procesa lectura │
    │   todo el        │          │  recién llegada  │
    │   historial)     │          │  en segundos)    │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             ▼                             ▼
          ┌──────────────────────────────────┐
          │        Capa de Servicio          │
          │  (combina vista batch + speed)   │
          └────────────────┬─────────────────┘
                           ▼
                   Consultas / Dashboards
```

### Escenario B — una sola lógica + conservar mediciones para reprocesar

**Elijo arquitectura Kappa.**

Kappa usa **una sola** línea de procesamiento (streaming) para todo.
Las mediciones se guardan en un log inmutable (típicamente Kafka con
retención larga); si cambia la lógica o aparece un bug, se "re-reproduce"
el log desde el inicio con el nuevo código. No hay doble implementación
batch + streaming como en Lambda.

Encaja perfectamente con el escenario: una sola lógica + poder reprocesar
el histórico.

```
    ┌─────────────┐
    │  Sensores   │
    └──────┬──────┘
           ▼
    ┌─────────────────────┐
    │  Log de eventos     │  ← guarda TODAS las mediciones
    │  (Kafka, inmutable) │     para poder reprocesarlas
    └──────────┬──────────┘
               ▼
    ┌─────────────────────┐
    │  Procesador único   │  ← misma lógica para lectura
    │  (streaming)        │     nueva y para reproceso
    └──────────┬──────────┘
               ▼
       Vista servida / Alertas
```

---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Descriptiva — qué pasó (hallazgos reales de este análisis)

1. **Planta_3 es la planta con más alertas de temperatura: 1,777 lecturas
   superaron los 85 °C, frente a un total general de 6,954 alertas
   repartidas entre las cuatro plantas.** Esto representa cerca del
   25.6 % de todas las alertas concentradas en una sola planta.

2. **La temperatura máxima registrada fue de 104.99 °C y ocurrió en
   4 lecturas distintas** (empate), tres de ellas en Planta_2 y Planta_3
   los días 1 y 2 de septiembre de 2026. El promedio general por planta
   se mantiene estable entre 66.5 °C y 66.8 °C, muy por debajo del
   umbral, lo que indica que las alertas son eventos puntuales, no una
   condición permanente.

### Predictiva — qué podría ocurrir

**Pregunta:** ¿Qué sensores de Planta_3 tienen la mayor probabilidad de
reportar una lectura > 95 °C en los próximos 7 días?

**Datos adicionales que necesitaría para investigarla:**

- Histórico de al menos varios meses (no solo los dos días del CSV actual).
- Lecturas de **vibración** correlacionadas con los picos de temperatura.
- Registro de **mantenimientos** realizados (fecha, sensor intervenido, tipo de servicio).
- **Condiciones ambientales** externas (temperatura ambiente, carga de producción).
- Metadatos del sensor: antigüedad, modelo, último recalibrado.

Con eso podría entrenar un modelo (regresión logística, árboles de decisión
o series de tiempo) que estime la probabilidad de una lectura peligrosa.

### Prescriptiva — qué conviene hacer

**Acción propuesta:** programar una inspección preventiva en los 10
sensores de Planta_3 que acumulan más alertas, antes del próximo turno
de alta carga.

**Información a revisar antes de decidir:**

- Confirmar que las alertas no se concentran en un **solo sensor** (en cuyo
  caso podría ser descalibración, no un problema real de la máquina).
- Revisar el **patrón horario**: ¿las alertas ocurren siempre en los
  mismos turnos? Eso apuntaría a sobrecarga operativa, no a falla.
- Consultar el **último reporte de mantenimiento** de cada máquina
  involucrada.
- Validar con el **jefe de planta** el costo del paro vs el riesgo de
  continuar operando.

> ⚠️ Una lectura por encima del umbral indica una **alerta del ejercicio**;
> por sí sola no demuestra que una máquina vaya a fallar. La decisión
> final debe apoyarse en información adicional antes de parar la producción.
