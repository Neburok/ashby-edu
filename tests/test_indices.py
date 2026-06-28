"""Tests para ashby_edu.indices.

TDD: estos tests se escriben ANTES de la implementación.
Cobertura:
- AVAILABLE_INDICES estructura y claves requeridas.
- Cada índice calcula el valor esperado (np.isclose).
- compute_index añade columna con el valor correcto.
- compute_index con index_name="all" añade todas las columnas.
- _safe_compute devuelve NaN si faltan columnas requeridas.
- compute_index con índice inexistente lanza KeyError.
"""
import numpy as np
import pandas as pd
import pytest

from ashby_edu import indices
from ashby_edu.indices import AVAILABLE_INDICES, compute_index


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def df_material():
    """DataFrame de materiales con todas las columnas del esquema real."""
    return pd.DataFrame(
        {
            "material": ["Acero", "Aluminio", "Titanio"],
            "sigma_y_MPa": [250.0, 95.0, 830.0],
            "E_GPa": [210_000.0, 69_000.0, 116_000.0],
            "sigma_UTS_MPa": [450.0, 115.0, 950.0],
            "densidad_gcm3": [7.85, 2.70, 4.51],
            "costo_USD_kg": [1.0, 3.0, 25.0],
        }
    )


# ---------------------------------------------------------------------------
# Estructura de AVAILABLE_INDICES
# ---------------------------------------------------------------------------

EXPECTED_INDICES = [
    "sigma_y_sobre_rho",
    "E_sobre_rho",
    "sigma_y_sobre_E",
    "sigma_UTS_sobre_rho",
    "E_sobre_rho_cubed",
    "sigma_y_sobre_rho_squared",
    "costo_sobre_sigma_y",
    "E_sobre_costo",
]


def test_available_indices_tiene_al_menos_8():
    assert len(AVAILABLE_INDICES) >= 8


def test_available_indices_contiene_los_requeridos():
    for name in EXPECTED_INDICES:
        assert name in AVAILABLE_INDICES, f"Falta índice: {name}"


@pytest.mark.parametrize("name", EXPECTED_INDICES)
def test_entrada_tiene_campos_obligatorios(name):
    spec = AVAILABLE_INDICES[name]
    assert "label" in spec and isinstance(spec["label"], str) and spec["label"]
    assert "formula" in spec and isinstance(spec["formula"], str) and spec["formula"]
    assert "requires" in spec and isinstance(spec["requires"], list) and spec["requires"]
    assert "compute" in spec and callable(spec["compute"])


# ---------------------------------------------------------------------------
# Cálculo individual de cada índice (valores esperados)
# ---------------------------------------------------------------------------

def test_sigma_y_sobre_rho(df_material):
    df = df_material
    out = compute_index(df, "sigma_y_sobre_rho")
    col = "M_sigma_y_sobre_rho"
    assert col in out.columns
    expected = df["sigma_y_MPa"] / df["densidad_gcm3"]
    assert np.allclose(out[col].values, expected.values)


def test_E_sobre_rho(df_material):
    df = df_material
    out = compute_index(df, "E_sobre_rho")
    col = "M_E_sobre_rho"
    assert col in out.columns
    expected = df["E_GPa"] / df["densidad_gcm3"]
    assert np.allclose(out[col].values, expected.values)


def test_sigma_y_sobre_E(df_material):
    df = df_material
    out = compute_index(df, "sigma_y_sobre_E")
    col = "M_sigma_y_sobre_E"
    assert col in out.columns
    expected = df["sigma_y_MPa"] / df["E_GPa"]
    assert np.allclose(out[col].values, expected.values)


def test_sigma_UTS_sobre_rho(df_material):
    df = df_material
    out = compute_index(df, "sigma_UTS_sobre_rho")
    col = "M_sigma_UTS_sobre_rho"
    assert col in out.columns
    expected = df["sigma_UTS_MPa"] / df["densidad_gcm3"]
    assert np.allclose(out[col].values, expected.values)


def test_E_sobre_rho_cubed(df_material):
    df = df_material
    out = compute_index(df, "E_sobre_rho_cubed")
    col = "M_E_sobre_rho_cubed"
    assert col in out.columns
    expected = df["E_GPa"] / (df["densidad_gcm3"] ** 3)
    assert np.allclose(out[col].values, expected.values)


def test_sigma_y_sobre_rho_squared(df_material):
    df = df_material
    out = compute_index(df, "sigma_y_sobre_rho_squared")
    col = "M_sigma_y_sobre_rho_squared"
    assert col in out.columns
    expected = df["sigma_y_MPa"] / (df["densidad_gcm3"] ** 2)
    assert np.allclose(out[col].values, expected.values)


def test_costo_sobre_sigma_y(df_material):
    df = df_material
    out = compute_index(df, "costo_sobre_sigma_y")
    col = "M_costo_sobre_sigma_y"
    assert col in out.columns
    expected = df["costo_USD_kg"] / df["sigma_y_MPa"]
    assert np.allclose(out[col].values, expected.values)


def test_E_sobre_costo(df_material):
    df = df_material
    out = compute_index(df, "E_sobre_costo")
    col = "M_E_sobre_costo"
    assert col in out.columns
    expected = df["E_GPa"] / df["costo_USD_kg"]
    assert np.allclose(out[col].values, expected.values)


# ---------------------------------------------------------------------------
# compute_index con "all"
# ---------------------------------------------------------------------------

def test_compute_index_all_anade_todas_las_columnas(df_material):
    out = compute_index(df_material, "all")
    for name in AVAILABLE_INDICES:
        col = f"M_{name}"
        assert col in out.columns, f"Falta columna {col}"


def test_compute_index_all_no_modifica_df_original(df_material):
    df_orig = df_material.copy()
    compute_index(df_material, "all")
    pd.testing.assert_frame_equal(df_material, df_orig)


def test_compute_index_single_no_modifica_df_original(df_material):
    df_orig = df_material.copy()
    compute_index(df_material, "sigma_y_sobre_rho")
    pd.testing.assert_frame_equal(df_material, df_orig)


# ---------------------------------------------------------------------------
# Columnas faltantes -> NaN (no error)
# ---------------------------------------------------------------------------

def test_safe_compute_devuelve_nan_si_falta_columna():
    df = pd.DataFrame({"sigma_y_MPa": [100.0], "E_GPa": [200_000.0]})
    spec = {
        "label": "test",
        "formula": "x/y",
        "requires": ["sigma_y_MPa", "densidad_gcm3"],
        "compute": lambda d: d["sigma_y_MPa"] / d["densidad_gcm3"],
    }
    series = indices._safe_compute(df, spec)
    assert len(series) == 1
    assert np.isnan(series.iloc[0])


def test_compute_index_falta_columna_devuelve_nan(df_material):
    df = df_material.drop(columns=["densidad_gcm3"])
    out = compute_index(df, "sigma_y_sobre_rho")
    col = "M_sigma_y_sobre_rho"
    assert col in out.columns
    assert np.all(np.isnan(out[col].values))


# ---------------------------------------------------------------------------
# Errores esperados
# ---------------------------------------------------------------------------

def test_compute_index_nombre_invalido_lanza_KeyError(df_material):
    with pytest.raises(KeyError):
        compute_index(df_material, "no_existe")


def test_compute_index_nan_propagacion(df_material):
    # Introducir NaN en densidad y verificar propagación natural
    df = df_material.copy()
    df.loc[0, "densidad_gcm3"] = np.nan
    out = compute_index(df, "sigma_y_sobre_rho")
    col = "M_sigma_y_sobre_rho"
    assert np.isnan(out[col].iloc[0])
    assert not np.isnan(out[col].iloc[1])