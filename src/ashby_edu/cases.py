"""Capa de carga de casos industriales para Ashby Edu.

Abstrae la fuente de casos (YAML en v1) de modo que la migración futura
a una base de datos solo requiera cambiar este módulo.
"""
from __future__ import annotations

from pathlib import Path

import yaml

__all__ = ["load_cases", "get_case_by_id", "list_case_names"]


def load_cases(path: str | Path | None = None) -> list[dict]:
    """Carga la lista de casos industriales desde un archivo YAML.

    Parameters
    ----------
    path : str | Path | None
        Ruta al YAML. Si es ``None``, busca ``data/casos.yaml`` relativo
        al paquete (tres niveles arriba de este módulo).

    Returns
    -------
    list[dict]
        Lista de casos; cada caso es un diccionario con las claves
        ``id``, ``nombre``, ``sector``, ``funcion``, ``proceso``,
        ``volumen``, ``restricciones``, ``normas``, ``candidatos``,
        ``ashby_config`` y ``es_rector``.
    """
    if path is None:
        path = Path(__file__).resolve().parent.parent.parent / "data" / "casos.yaml"
    path = Path(path)

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError(
            f"Se esperaba una lista de casos en {path}, se obtuvo {type(data).__name__}"
        )

    return data


def get_case_by_id(cases: list[dict], case_id: str) -> dict | None:
    """Busca un caso por su ``id`` exacto.

    Devuelve el primer dict que coincide o ``None`` si no existe.
    """
    for c in cases:
        if c.get("id") == case_id:
            return c
    return None


def list_case_names(cases: list[dict]) -> list[str]:
    """Devuelve la lista de ``nombre`` de los casos, en el mismo orden."""
    return [c["nombre"] for c in cases]