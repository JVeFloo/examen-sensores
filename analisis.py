"""
Análisis del CSV de sensores industriales.

Lee data/sensores_industriales.csv, calcula los resultados pedidos
e imprime el reporte en consola. También exporta las lecturas con
alerta de temperatura a resultados/alertas.csv.

Solo usa la biblioteca estándar de Python (no requiere dependencias
externas).
"""

import csv
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas relativas (el script funciona desde cualquier máquina que lo clone)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
RUTA_CSV = BASE_DIR / "data" / "sensores_industriales.csv"
RUTA_SALIDA = BASE_DIR / "resultados" / "alertas.csv"

# Umbral didáctico definido en el examen
UMBRAL_TEMP = 85.0

# Columnas originales del CSV (orden a conservar en la exportación)
COLUMNAS = ["id_registro", "fecha_hora", "id_sensor", "planta",
            "temperatura_c", "vibracion_mm_s"]


def main():
    # -----------------------------------------------------------------------
    # 1. Leer el CSV completo a memoria
    # -----------------------------------------------------------------------
    with open(RUTA_CSV, "r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        filas = list(lector)

    # Convertir las columnas numéricas de texto a float
    for fila in filas:
        fila["temperatura_c"] = float(fila["temperatura_c"])
        fila["vibracion_mm_s"] = float(fila["vibracion_mm_s"])

    print("=" * 60)
    print(" ANÁLISIS DE SENSORES INDUSTRIALES")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 2. Cantidad de registros y de sensores distintos
    # -----------------------------------------------------------------------
    total_registros = len(filas)
    sensores_distintos = len({f["id_sensor"] for f in filas})
    print(f"\n[1] Total de registros : {total_registros:,}")
    print(f"    Sensores distintos : {sensores_distintos}")

    # -----------------------------------------------------------------------
    # 3. Temperatura promedio por planta
    # -----------------------------------------------------------------------
    suma_por_planta = defaultdict(float)
    conteo_por_planta = defaultdict(int)
    for fila in filas:
        suma_por_planta[fila["planta"]] += fila["temperatura_c"]
        conteo_por_planta[fila["planta"]] += 1

    print("\n[2] Temperatura promedio por planta (°C):")
    for planta in sorted(suma_por_planta):
        promedio = suma_por_planta[planta] / conteo_por_planta[planta]
        print(f"    {planta} : {round(promedio, 2)}")

    # -----------------------------------------------------------------------
    # 4. Temperatura máxima + sensor y fecha correspondientes
    #    (si hay empates se muestran todos)
    # -----------------------------------------------------------------------
    temp_max = max(f["temperatura_c"] for f in filas)
    filas_max = [f for f in filas if f["temperatura_c"] == temp_max]
    print(f"\n[3] Temperatura máxima registrada: {temp_max} °C")
    print(f"    Lecturas con ese valor ({len(filas_max)}):")
    for f in filas_max:
        print(f"      - Sensor {f['id_sensor']} "
              f"en {f['planta']} el {f['fecha_hora']}")

    # -----------------------------------------------------------------------
    # 5. Cuántas lecturas superan el umbral de 85 °C
    # -----------------------------------------------------------------------
    alertas = [f for f in filas if f["temperatura_c"] > UMBRAL_TEMP]
    print(f"\n[4] Lecturas con temperatura > {UMBRAL_TEMP} °C : {len(alertas):,}")

    # -----------------------------------------------------------------------
    # 6. Planta(s) con más alertas (con empates si los hay)
    # -----------------------------------------------------------------------
    conteo_alertas = defaultdict(int)
    for f in alertas:
        conteo_alertas[f["planta"]] += 1

    max_alertas = max(conteo_alertas.values())
    plantas_top = sorted(p for p, c in conteo_alertas.items() if c == max_alertas)

    print(f"\n[5] Planta(s) con más alertas ({max_alertas} alertas):")
    for planta in plantas_top:
        print(f"    {planta} : {max_alertas}")

    # -----------------------------------------------------------------------
    # 7. Exportar las lecturas con alerta a resultados/alertas.csv
    # -----------------------------------------------------------------------
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8", newline="") as f_out:
        escritor = csv.DictWriter(f_out, fieldnames=COLUMNAS)
        escritor.writeheader()
        for fila in alertas:
            escritor.writerow(fila)

    print(f"\n[6] Alertas exportadas a: {RUTA_SALIDA.relative_to(BASE_DIR)}")
    print(f"    Filas exportadas: {len(alertas):,}")

    print("\n" + "=" * 60)
    print(" ANÁLISIS TERMINADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
