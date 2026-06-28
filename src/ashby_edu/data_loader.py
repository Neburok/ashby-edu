"""Capa de carga de datos de materiales.

Abstrae la fuente de datos (CSV en v1) para que la migración futura a
SQLite/PostgreSQL solo requiera cambiar este módulo.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

__all__ = ["load_materials", "get_material_by_name", "list_families", "NUMERIC_COLS"]


# Columnas que deben ser numéricas (del esquema 29-columnas del 102)
NUMERIC_COLS = [
    "densidad_gcm3",
    "E_GPa",
    "sigma_y_MPa",
    "sigma_UTS_MPa",
    "elongacion_pct",
    "dureza_HB",
    "dureza_HRC",
    "k_WmK",
    "alfa_1e-6C",
    "T_fusion_C",
    "T_max_servicio_C",
    "costo_USD_kg",
    "energia_embebida_MJkg",
    "huella_CO2_kgCO2kg",
]


def load_materials(path: str | Path | None = None) -> pd.DataFrame:
    """Carga la base de datos de materiales desde CSV.

    Parameters
    ----------
    path : str | Path | None
        Ruta al CSV. Si es None, busca ``data/materiales.csv`` relativo
        al paquete (tres niveles arriba de este módulo).

    Returns
    -------
    pandas.DataFrame
        DataFrame con todas las columnas, tipos numéricos convertidos.
    """
    if path is None:
        path = Path(__file__).resolve().parent.parent.parent / "data" / "materiales.csv"
    path = Path(path)

    df = pd.read_csv(path)

    # Convertir columnas numéricas
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_material_by_name(df: pd.DataFrame, name: str) -> pd.Series | None:
    """Busca un material por nombre exacto.

    Devuelve la primera fila que coincide o ``None`` si no existe.
    """
    matches = df[df["material"] == name]
    if matches.empty:
        return None
    return matches.iloc[0]


def list_families(df: pd.DataFrame) -> list[str]:
    """Devuelve lista ordenada de familias presentes en el DataFrame."""
    return sorted(df["familia"].dropna().unique().tolist())