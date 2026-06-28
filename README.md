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

## Licencia

MIT