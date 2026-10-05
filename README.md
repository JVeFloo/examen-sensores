# Análisis de Sensores Industriales

Proyecto académico para la materia **Fundamentos de Big Data** (UPQ, IDIA 224).
Analiza un archivo CSV con mediciones de temperatura y vibración provenientes
de sensores instalados en cuatro plantas industriales.

> ⚠️ **Nota:** Los datos del CSV son **simulados** con fines didácticos.
> No corresponden a mediciones reales de ninguna empresa.

---

## 📊 Datos

El archivo `data/sensores_industriales.csv` contiene 100,000 mediciones
con las siguientes columnas:

| Columna          | Significado                          |
|------------------|--------------------------------------|
| `id_registro`    | Identificador único de la medición   |
| `fecha_hora`     | Fecha y hora de la lectura           |
| `id_sensor`      | Identificador del sensor             |
| `planta`         | Planta donde está instalado el sensor|
| `temperatura_c`  | Temperatura en grados Celsius        |
| `vibracion_mm_s` | Vibración en milímetros por segundo  |

Para este ejercicio se considera **alerta de temperatura** toda lectura
mayor que **85 °C**.

---

## 🎯 Objetivo

Que el programa `analisis.py` responda, a partir del CSV:

1. Cantidad total de registros y de sensores distintos.
2. Temperatura promedio por planta.
3. Temperatura máxima registrada, con sensor y fecha correspondientes.
4. Número de lecturas por encima del umbral de alerta.
5. Planta con la mayor cantidad de alertas.
6. Exportar todas las lecturas con alerta a `resultados/alertas.csv`.

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd examen-sensores
```

### 2. Crear y activar el entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

Este proyecto **no requiere dependencias externas**: utiliza
únicamente la biblioteca estándar de Python (módulos `csv`,
`collections` y `pathlib`). El archivo `requirements.txt` se
incluye por convención pero está vacío de paquetes.

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el análisis

```bash
python analisis.py
```

Al terminar se genera `resultados/alertas.csv` con todas las lecturas que
superaron el umbral de 85 °C.

---

## 📁 Estructura del proyecto

```
examen-sensores/
├── data/
│   └── sensores_industriales.csv
├── resultados/
│   └── alertas.csv              (se genera al correr analisis.py)
├── evidencias/
│   └── captura.png              (reproducibilidad en segunda copia)
├── analisis.py
├── informe.md
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 👥 Equipo

- **Jeshua Vera Flores** — IDIA 224
- **Betel Zurisadai Hernández Sánchez** — IDIA 224

Universidad Politécnica de Querétaro
