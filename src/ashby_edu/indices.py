"""Índices de desempeño de Ashby para selección de materiales.

Cada índice es de la forma M = f(propiedades) y se expresa como un
diccionario de especificación (``AVAILABLE_INDICES``) que el resto de la
app consume para calcularlos sobre un DataFrame de materiales.

Convención de columnas de salida: ``M_<index_name>``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["AVAILABLE_INDICES", "compute_index"]


# ---------------------------------------------------------------------------
# Helper interno
# ---------------------------------------------------------------------------

def _safe_compute(df: pd.DataFrame, spec: dict) -> pd.Series:
    """Ejecuta ``spec["compute"]`` solo si todas las columnas requeridas existen.

    Si falta alguna columna requerida, devuelve una Serie de NaN del mismo
    largo que ``df`` (nunca lanza un error por columnas ausentes).
    """
    missing = [c for c in spec["requires"] if c not in df.columns]
    if missing:
        return pd.Series(np.nan, index=df.index, dtype=float)
    result = spec["compute"](df)
    # Asegurar que devolvemos una Series alineada al índice del DataFrame
    if not isinstance(result, pd.Series):
        result = pd.Series(result, index=df.index)
    return result


# ---------------------------------------------------------------------------
# Catálogo de índices
# ---------------------------------------------------------------------------

AVAILABLE_INDICES: dict[str, dict] = {
    "sigma_y_sobre_rho": {
        "label": "Resistencia específica (σ_y/ρ)",
        "formula": "σ_y / ρ",
        "requires": ["sigma_y_MPa", "densidad_gcm3"],
        "compute": lambda d: d["sigma_y_MPa"] / d["densidad_gcm3"],
    },
    "E_sobre_rho": {
        "label": "Rigidez específica (E/ρ)",
        "formula": "E / ρ",
        "requires": ["E_GPa", "densidad_gcm3"],
        "compute": lambda d: d["E_GPa"] / d["densidad_gcm3"],
    },
    "sigma_y_sobre_E": {
        "label": "Límite elástico sobre módulo (σ_y/E)",
        "formula": "σ_y / E",
        "requires": ["sigma_y_MPa", "E_GPa"],
        "compute": lambda d: d["sigma_y_MPa"] / d["E_GPa"],
    },
    "sigma_UTS_sobre_rho": {
        "label": "Resistencia última específica (σ_UTS/ρ)",
        "formula": "σ_UTS / ρ",
        "requires": ["sigma_UTS_MPa", "densidad_gcm3"],
        "compute": lambda d: d["sigma_UTS_MPa"] / d["densidad_gcm3"],
    },
    "E_sobre_rho_cubed": {
        "label": "Viga en flexión, mínima masa (E/ρ³)",
        "formula": "E / ρ³",
        "requires": ["E_GPa", "densidad_gcm3"],
        "compute": lambda d: d["E_GPa"] / (d["densidad_gcm3"] ** 3),
    },
    "sigma_y_sobre_rho_squared": {
        "label": "Panel a tracción, mínima masa (σ_y/ρ²)",
        "formula": "σ_y / ρ²",
        "requires": ["sigma_y_MPa", "densidad_gcm3"],
        "compute": lambda d: d["sigma_y_MPa"] / (d["densidad_gcm3"] ** 2),
    },
    "costo_sobre_sigma_y": {
        "label": "Costo por unidad de resistencia (costo/σ_y)",
        "formula": "costo / σ_y",
        "requires": ["costo_USD_kg", "sigma_y_MPa"],
        "compute": lambda d: d["costo_USD_kg"] / d["sigma_y_MPa"],
    },
    "E_sobre_costo": {
        "label": "Rigidez por unidad de costo (E/costo)",
        "formula": "E / costo",
        "requires": ["E_GPa", "costo_USD_kg"],
        "compute": lambda d: d["E_GPa"] / d["costo_USD_kg"],
    },
}


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def compute_index(df: pd.DataFrame, index_name: str) -> pd.DataFrame:
    """Calcula uno o todos los índices de Ashby sobre ``df``.

    Parámetros
    ----------
    df : pandas.DataFrame
        DataFrame de materiales. La fila es cada material y las columnas son
        propiedades (``sigma_y_MPa``, ``E_GPa``, ``densidad_gcm3``,
        ``sigma_UTS_MPa``, ``costo_USD_kg``...).
    index_name : str
        Nombre del índice (clave de ``AVAILABLE_INDICES``) o ``"all"`` para
        calcular todos los índices disponibles.

    Devuelve
    --------
    pandas.DataFrame
        Una **copia** de ``df`` con la(s) nueva(s) columna(s) ``M_<index>``.
        Si faltan columnas requeridas, el valor correspondiente es ``NaN``
        (nunca se lanza un error por datos ausentes).

    Excepciones
    -----------
    KeyError
        Si ``index_name`` no es ``"all"`` ni una clave válida de
        ``AVAILABLE_INDICES``.
    """
    out = df.copy()

    if index_name == "all":
        names = list(AVAILABLE_INDICES.keys())
    else:
        if index_name not in AVAILABLE_INDICES:
            raise KeyError(
                f"Índice '{index_name}' no existe. "
                f"Disponibles: {', '.join(AVAILABLE_INDICES)}"
            )
        names = [index_name]

    for name in names:
        spec = AVAILABLE_INDICES[name]
        col = f"M_{name}"
        out[col] = _safe_compute(out, spec)

    return out