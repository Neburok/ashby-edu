"""Tests para ashby_edu.ashby_chart.

TDD: estos tests se escriben ANTES de la implementación.
Cobertura:
- create_ashby_chart devuelve go.Figure.
- Escala log-log en ambos ejes.
- Burbujas coloreadas por familia con la config de colores/marcadores.
- df_candidates superpuesto con borde negro grueso, color gold, más grandes.
- Línea de índice (y = intercept * x^slope) cuando se pasan slope/intercept.
- Labels de materiales como texto junto a las burbujas.
- Layout: template='plotly_white', height=700, legend horizontal arriba.
- Hovertemplate mostrando nombre del material y valores x,y.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from ashby_edu.ashby_chart import create_ashby_chart


# ---------------------------------------------------------------------------
# Config esperada
# ---------------------------------------------------------------------------

EXPECTED_COLORS = {
    "metal_ferroso": "#2563EB",
    "metal_no_ferroso": "#60A5FA",
    "ceramico": "#F97316",
    "polimero": "#22C55E",
    "compuesto": "#A855F7",
    "natural": "#8B7355",
    "elastomero": "#EC4899",
}

EXPECTED_MARKERS = {
    "metal_ferroso": "circle",
    "metal_no_ferroso": "circle",
    "ceramico": "square",
    "polimero": "triangle-up",
    "compuesto": "diamond",
    "natural": "star",
    "elastomero": "hexagon",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def df_material():
    """DataFrame con varias familias de materiales."""
    return pd.DataFrame(
        {
            "material": [
                "Acero 1020",
                "Aluminio 6061",
                "Alúmina",
                "PEHD",
                "Carbono/Epoxi",
                "Madera Roble",
                "Caucho NR",
            ],
            "familia": [
                "metal_ferroso",
                "metal_no_ferroso",
                "ceramico",
                "polimero",
                "compuesto",
                "natural",
                "elastomero",
            ],
            "densidad_gcm3": [7.85, 2.70, 3.9, 0.95, 1.6, 0.7, 0.92],
            "E_GPa": [200.0, 69.0, 380.0, 0.8, 140.0, 12.0, 0.01],
            "sigma_y_MPa": [250.0, 240.0, np.nan, 22.0, 1000.0, 40.0, 2.0],
        }
    )


@pytest.fixture
def df_candidates():
    return pd.DataFrame(
        {
            "material": ["Aluminio 6061", "Carbono/Epoxi"],
            "familia": ["metal_no_ferroso", "compuesto"],
            "densidad_gcm3": [2.70, 1.6],
            "E_GPa": [69.0, 140.0],
            "sigma_y_MPa": [240.0, 1000.0],
        }
    )


# ---------------------------------------------------------------------------
# Tests básicos
# ---------------------------------------------------------------------------

def test_devuelve_go_figure(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    assert isinstance(fig, go.Figure)


def test_ejes_loglog(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    xaxis = fig.layout.xaxis
    yaxis = fig.layout.yaxis
    assert xaxis.type == "log"
    assert yaxis.type == "log"


def test_titulo_por_defecto(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    assert "Ashby" in (fig.layout.title.text or "")


def test_titulo_personalizado(df_material):
    fig = create_ashby_chart(
        df_material, "densidad_gcm3", "E_GPa", title="Mi Título"
    )
    assert fig.layout.title.text == "Mi Título"


def test_labels_ejes_personalizados(df_material):
    fig = create_ashby_chart(
        df_material, "densidad_gcm3", "E_GPa", x_label="Densidad", y_label="Módulo"
    )
    assert fig.layout.xaxis.title.text == "Densidad"
    assert fig.layout.yaxis.title.text == "Módulo"


def test_labels_ejes_por_defecto_usa_col_name(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    assert fig.layout.xaxis.title.text == "densidad_gcm3"
    assert fig.layout.yaxis.title.text == "E_GPa"


def test_layout_template(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    # Plotly convierte "plotly_white" en un objeto Template; verificamos el
    # nombre del theme almacenado en fig.layout.template.layout (si existe)
    # o usamos la inspección por to_dict.
    tmpl = fig.layout.template
    # puede ser str (Template) o un objeto Template de plotly
    try:
        name = tmpl.layout.setdefault.__qualname__  # not reliable
    except AttributeError:
        name = None
    # Método robusto: serializar a dict y buscar el nombre del template
    repr_str = str(tmpl.to_dict()) if hasattr(tmpl, "to_dict") else str(tmpl)
    # Si el template es 'plotly_white', no tendremos 'dark' ni 'ggplot2';
    # además la cuadrícula es clara (#EBF0F8) y el fondo blanco.
    assert "'#EBF0F8'" in repr_str or "plotly_white" in repr_str


def test_layout_height(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    assert fig.layout.height == 700


def test_legend_horizontal_arriba(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    assert fig.layout.legend.orientation == "h"
    # valign top o y alto
    assert fig.layout.legend.y is not None and fig.layout.legend.y >= 0.95


# ---------------------------------------------------------------------------
# Trazas por familia
# ---------------------------------------------------------------------------

def test_un_trace_por_familia_presente(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    families_present = set(df_material["familia"].unique())
    scatter_names = {tr.name for tr in fig.data if isinstance(tr, go.Scatter)}
    assert families_present.issubset(scatter_names)


def test_color_por_familia(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    for tr in fig.data:
        if tr.name in EXPECTED_COLORS:
            assert tr.marker.color == EXPECTED_COLORS[tr.name]


def test_marker_symbol_por_familia(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    for tr in fig.data:
        if tr.name in EXPECTED_MARKERS:
            assert tr.marker.symbol == EXPECTED_MARKERS[tr.name]


def test_solo_familias_presentes_como_traces(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    scatter_names = {tr.name for tr in fig.data if isinstance(tr, go.Scatter)}
    # No se crean traces para familias ausentes del df
    assert "metal_ferroso" in scatter_names
    assert "elastomero" in scatter_names


# ---------------------------------------------------------------------------
# Hovertemplate
# ---------------------------------------------------------------------------

def test_hovertemplate_contiene_material_y_valores(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    for tr in fig.data:
        if isinstance(tr, go.Scatter) and tr.mode and "text" not in (tr.mode or ""):
            # hovertemplate debe referenciar nombre y x,y
            ht = tr.hovertemplate or ""
            assert "material" in ht.lower() or "%{text}" in ht or "customdata" in ht
            assert "%{x}" in ht
            assert "%{y}" in ht


# ---------------------------------------------------------------------------
# Labels de materiales
# ---------------------------------------------------------------------------

def test_labels_materiales_activo(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa", label_materials=True)
    # Al menos un trace debe tener mode con "text"
    has_text = any(
        isinstance(tr, go.Scatter) and tr.mode and "text" in tr.mode for tr in fig.data
    )
    assert has_text


def test_labels_materiales_desactivo(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa", label_materials=False)
    # Ningún trace debe tener modo "text" puro (markers sí)
    for tr in fig.data:
        if isinstance(tr, go.Scatter):
            assert tr.mode is None or "text" not in (tr.mode or "")


# ---------------------------------------------------------------------------
# df_candidates
# ---------------------------------------------------------------------------

def test_candidates_agrega_trace(df_material, df_candidates):
    fig = create_ashby_chart(
        df_material, "densidad_gcm3", "E_GPa", df_candidates=df_candidates
    )
    # Debe existir un trace con color gold
    has_gold = any(
        isinstance(tr, go.Scatter) and tr.marker.color == "gold" for tr in fig.data
    )
    assert has_gold


def test_candidates_borde_negro_grueso(df_material, df_candidates):
    fig = create_ashby_chart(
        df_material, "densidad_gcm3", "E_GPa", df_candidates=df_candidates
    )
    for tr in fig.data:
        if isinstance(tr, go.Scatter) and tr.marker.color == "gold":
            assert tr.marker.line.color == "black" or tr.marker.line.color == "#000000"
            assert tr.marker.line.width >= 2


def test_candidates_marcadores_mas_grandes(df_material, df_candidates):
    fig = create_ashby_chart(
        df_material, "densidad_gcm3", "E_GPa", df_candidates=df_candidates
    )
    family_sizes = [
        tr.marker.size
        for tr in fig.data
        if isinstance(tr, go.Scatter)
        and tr.marker.color != "gold"
        and tr.marker.size is not None
    ]
    for tr in fig.data:
        if isinstance(tr, go.Scatter) and tr.marker.color == "gold":
            cand_size = tr.marker.size
            assert cand_size is not None
            # Mayor que el tamaño de las burbujas de familia (si son numéricas)
            if family_sizes and all(isinstance(s, (int, float)) for s in family_sizes):
                assert cand_size > max(family_sizes)


# ---------------------------------------------------------------------------
# Línea de índice
# ---------------------------------------------------------------------------

def test_index_line_agrega_trace(df_material):
    fig = create_ashby_chart(
        df_material,
        "densidad_gcm3",
        "E_GPa",
        index_line_slope=2.0,
        index_line_intercept=1e3,
    )
    # Debe haber un trace con mode "lines"
    has_line = any(
        isinstance(tr, go.Scatter) and tr.mode and "lines" in tr.mode
        for tr in fig.data
    )
    assert has_line


def test_index_line_valores_correctos(df_material):
    slope = 2.0
    intercept = 1e3
    fig = create_ashby_chart(
        df_material,
        "densidad_gcm3",
        "E_GPa",
        index_line_slope=slope,
        index_line_intercept=intercept,
    )
    # Encontrar el trace de la línea (mode lines)
    line_tr = None
    for tr in fig.data:
        if isinstance(tr, go.Scatter) and tr.mode and "lines" in tr.mode:
            line_tr = tr
            break
    assert line_tr is not None
    xs = np.array(line_tr.x, dtype=float)
    ys = np.array(line_tr.y, dtype=float)
    expected = intercept * (xs ** slope)
    assert np.allclose(ys, expected)


def test_sin_index_line_si_no_se_pasa(df_material):
    fig = create_ashby_chart(df_material, "densidad_gcm3", "E_GPa")
    has_line = any(
        isinstance(tr, go.Scatter) and tr.mode and "lines" in tr.mode
        for tr in fig.data
    )
    assert not has_line


def test_index_line_usa_rango_x_del_df(df_material):
    slope = 2.0
    intercept = 1e3
    fig = create_ashby_chart(
        df_material,
        "densidad_gcm3",
        "E_GPa",
        index_line_slope=slope,
        index_line_intercept=intercept,
    )
    line_tr = None
    for tr in fig.data:
        if isinstance(tr, go.Scatter) and tr.mode and "lines" in tr.mode:
            line_tr = tr
            break
    xs = np.array(line_tr.x, dtype=float)
    assert xs.min() <= df_material["densidad_gcm3"].min()
    assert xs.max() >= df_material["densidad_gcm3"].max()


# ---------------------------------------------------------------------------
# Sin columna "material" — no debe romper
# ---------------------------------------------------------------------------

def test_sin_columna_material_no_rompe():
    df = pd.DataFrame(
        {
            "familia": ["metal_ferroso"],
            "densidad_gcm3": [7.85],
            "E_GPa": [200.0],
        }
    )
    fig = create_ashby_chart(df, "densidad_gcm3", "E_GPa")
    assert isinstance(fig, go.Figure)


def test_sin_columna_familia_no_rompe():
    df = pd.DataFrame(
        {
            "material": ["Acero"],
            "densidad_gcm3": [7.85],
            "E_GPa": [200.0],
        }
    )
    fig = create_ashby_chart(df, "densidad_gcm3", "E_GPa")
    assert isinstance(fig, go.Figure)