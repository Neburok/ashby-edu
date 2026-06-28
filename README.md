# Ashby Edu

App web interactiva para selección de materiales por método gráfico de Ashby,
enfocada a Ingeniería Industrial. Diseñada para fines didácticos en la UTEQ.

Sustituye a CES-Edupack con funciones enfocadas a aplicaciones industriales:
cartas de Ashby interactivas, índices de desempeño configurables, casos
industriales guiados, y base de datos abierta y extensible.

## Instalación

```bash
git clone git@github.com:Neburok/ashby-edu.git
cd ashby-edu
pip install -e ".[dev]"
```

## Ejecutar

```bash
streamlit run src/ashby_edu/app.py
```

La app abre en `http://localhost:8501`.

## Funcionalidades

### 📊 Carta de Ashby (modo libre)
- Selección de ejes X/Y entre propiedades físicas e índices de desempeño
- Burbujas coloreadas por familia (metales, polímeros, cerámicos, etc.)
- Líneas de índice de desempeño configurables (pendiente e intercepto)
- Selección de materiales candidatos para superponer
- Tabla comparativa de candidatos
- Exportar gráfica como PNG y candidatos como CSV

### 🏭 Casos Industriales (modo guiado)
- 10 casos industriales alineados a Ingeniería Industrial:
  carcasa de taladro, botella PET, tarima, tubería, engrane,
  gabinete NEMA, contenedor, rodillo, inserto de corte, licuadora
- Cada caso precarga la carta de Ashby con su configuración óptima
- Restricciones, normas y materiales candidatos documentados

### 📋 Base de Datos
- ~40 materiales en 7 familias
- 29 propiedades por material (mecánicas, térmicas, tecnológicas, económicas, ambientales)
- Buscador por nombre
- Selector de columnas a visualizar

## Base de datos de materiales

La base de datos vive en `data/materiales.csv` — un CSV con 29 columnas.

### Esquema de columnas

| Bloque | Columnas |
|---|---|
| Identidad | material, familia, densidad_gcm3, tipo_enlace, estructura_cristalina |
| Mecánicas | E_GPa, sigma_y_MPa, sigma_UTS_MPa, elongacion_pct, dureza_HB, dureza_HRC |
| Térmicas | k_WmK, alfa_1e-6C, T_fusion_C, T_max_servicio_C |
| Químicas | resistencia_corrosion (1-5) |
| Tecnológicas | maquinabilidad, soldabilidad, conformabilidad, colabilidad, templabilidad (1-5) |
| Económicas | costo_USD_kg, disponibilidad (1-3), formas_suministro |
| Ambientales | energia_embebida_MJkg, huella_CO2_kgCO2kg, reciclabilidad (1-5) |
| Normativas | normas_aplicables |
| Procedencia | notas_fuente |

### Cómo contribuir materiales

1. Abre `data/materiales.csv` en Excel, Google Sheets, o tu editor.
2. Añade una fila por material nuevo.
3. Envía un pull request.

## Índices de desempeño disponibles

| Índice | Fórmula | Aplicación |
|---|---|---|
| σ_y/ρ | Resistencia específica | Selección por resistencia-liviano |
| E/ρ | Rigidez específica | Selección por rigidez-liviano |
| σ_y/E | Resistencia por rigidez | Selección por deformación controlada |
| σ_UTS/ρ | Resistencia última específica | Falla frágil |
| E/ρ³ | Rigidez por Volkersen | Viga en flexión mínima masa |
| σ_y/ρ² | Panel a tracción | Panel mínima masa |
| costo/σ_y | Costo por resistencia | Selección económica |
| E/costo | Rigidez por costo | Selección económica |

## Despliegue (Streamlit Community Cloud)

1. Push a `main` en GitHub.
2. Conectar repo en [share.streamlit.io](https://share.streamlit.io).
3. Main file path: `src/ashby_edu/app.py`.
4. Deploy.

## Tests

```bash
python3 -m pytest -v
```

## Licencia

MIT — Libre uso educativo.