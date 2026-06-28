"""Generación de cartas de Ashby interactivas con Plotly.

Convierte la lógica de 102_ashby_grafica.py (matplotlib estático) a una figura
Plotly lista para Streamlit, con burbujas coloreadas por familia, líneas de
índice de desempeño, y superposición de candidatos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

__all__ = ["create_ashby_chart", "FAMILY_CONFIG"]


# Configuración de familias (colores del script 102 original)
FAMILY_CONFIG = {
    "metal_ferroso":     {"color": "#2563EB", "marker": "circle",       "label": "Metales ferrosos"},
    "metal_no_ferroso":  {"color": "#60A5FA", "marker": "circle",       "label": "Metales no ferrosos"},
    "ceramico":          {"color": "#F97316", "marker": "square",       "label": "Cerámicos"},
    "polimero":          {"color": "#22C55E", "marker": "triangle-up",  "label": "Polímeros"},
    "compuesto":         {"color": "#A855F7", "marker": "diamond",     "label": "Compuestos"},
    "natural":           {"color": "#8B7355", "marker": "star",        "label": "Naturales"},
    "elastomero":        {"color": "#EC4899", "marker": "hexagon",     "label": "Elastómeros"},
}

BUBBLE_BASE_SIZE = 20


def create_ashby_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    df_candidates: pd.DataFrame | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    title: str = "Carta de Ashby — Selección de Materiales",
    index_line_slope: float | None = None,
    index_line_intercept: float | None = None,
    label_materials: bool = True,
) -> go.Figure:
    """Crea una carta de Ashby interactiva con Plotly.

    Parameters
    ----------
    df : DataFrame
        Base de datos completa de materiales.
    x_col, y_col : str
        Columnas a graficar en cada eje.
    df_candidates : DataFrame | None
        Materiales candidatos a superponer (borde negro, más grandes).
    x_label, y_label : str | None
        Etiquetas de ejes. Si None, usa el nombre de la columna.
    title : str
        Título del gráfico.
    index_line_slope, index_line_intercept : float | None
        Si ambos son distintos de None, dibuja una línea de índice de
        desempeño: y = intercept * x^slope (escala log-log).
    label_materials : bool
        Si True, anota el nombre de cada material en la burbuja.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    df_plot = df.dropna(subset=[x_col, y_col]).copy()
    if df_plot.empty:
        fig.update_layout(title="Sin datos para graficar")
        return fig

    has_material_col = "material" in df_plot.columns
    has_familia_col = "familia" in df_plot.columns

    # ── Trazar cada familia como un trace separado ──
    if has_familia_col:
        for family, cfg in FAMILY_CONFIG.items():
            subset = df_plot[df_plot["familia"] == family]
            if subset.empty:
                continue

            text = subset["material"].tolist() if has_material_col and label_materials else None
            mode = "markers+text" if label_materials and has_material_col else "markers"

            fig.add_trace(go.Scatter(
                x=subset[x_col],
                y=subset[y_col],
                mode=mode,
                text=text,
                textposition="top center",
                textfont=dict(size=7),
                marker=dict(
                    size=BUBBLE_BASE_SIZE,
                    color=cfg["color"],
                    symbol=cfg["marker"],
                    line=dict(width=0.5, color="white"),
                    opacity=0.7,
                ),
                name=family,
                legendgroup=family,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{x_col}: %{{x:.2f}}<br>"
                    f"{y_col}: %{{y:.2f}}"
                    "<extra></extra>"
                ) if has_material_col else (
                    f"{x_col}: %{{x:.2f}}<br>"
                    f"{y_col}: %{{y:.2f}}"
                    "<extra></extra>"
                ),
            ))
    else:
        # Sin columna familia — dibujar todo como un solo trace
        text = df_plot["material"].tolist() if has_material_col and label_materials else None
        mode = "markers+text" if label_materials and has_material_col else "markers"

        fig.add_trace(go.Scatter(
            x=df_plot[x_col],
            y=df_plot[y_col],
            mode=mode,
            text=text,
            textposition="top center",
            textfont=dict(size=7),
            marker=dict(
                size=BUBBLE_BASE_SIZE,
                color="#60A5FA",
                line=dict(width=0.5, color="white"),
                opacity=0.7,
            ),
            name="Materiales",
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"{x_col}: %{{x:.2f}}<br>"
                f"{y_col}: %{{y:.2f}}"
                "<extra></extra>"
            ) if has_material_col else (
                f"{x_col}: %{{x:.2f}}<br>"
                f"{y_col}: %{{y:.2f}}"
                "<extra></extra>"
            ),
        ))

    # ── Superponer candidatos ──
    if df_candidates is not None:
        df_cand = df_candidates.dropna(subset=[x_col, y_col])
        if not df_cand.empty:
            cand_text = df_cand["material"].tolist() if "material" in df_cand.columns else None
            fig.add_trace(go.Scatter(
                x=df_cand[x_col],
                y=df_cand[y_col],
                mode="markers+text",
                text=cand_text,
                textposition="top center",
                textfont=dict(size=9, color="black"),
                marker=dict(
                    size=BUBBLE_BASE_SIZE * 1.5,
                    color="gold",
                    symbol="circle",
                    line=dict(width=3, color="black"),
                ),
                name="Mis candidatos",
                hovertemplate="<b>Candidato: %{text}</b><extra></extra>",
            ))

    # ── Línea de índice de desempeño ──
    if index_line_slope is not None and index_line_intercept is not None:
        x_min = df_plot[x_col].min() * 0.5
        x_max = df_plot[x_col].max() * 2
        x_line = np.logspace(np.log10(x_min), np.log10(x_max), 100)
        y_line = index_line_intercept * (x_line ** index_line_slope)
        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            line=dict(color="gray", width=1, dash="dash"),
            name=f"Índice: y = {index_line_intercept:.1f} · x^{index_line_slope:.1f}",
            hoverinfo="skip",
        ))

    # ── Layout ──
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(
            type="log",
            title=x_label or x_col,
            gridcolor="lightgray",
            gridwidth=0.5,
        ),
        yaxis=dict(
            type="log",
            title=y_label or y_col,
            gridcolor="lightgray",
            gridwidth=0.5,
        ),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        template="plotly_white",
        height=700,
    )

    return fig