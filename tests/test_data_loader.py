"""Tests para ashby_edu.data_loader."""
import pandas as pd
import pytest

from ashby_edu.data_loader import (
    load_materials,
    get_material_by_name,
    list_families,
)


def test_load_materials_returns_dataframe(tmp_path):
    """load_materials debe devolver un DataFrame con columnas esperadas."""
    csv = tmp_path / "materiales.csv"
    csv.write_text(
        "material,familia,densidad_gcm3,tipo_enlace\n"
        "Aluminio 1100,metal_no_ferroso,2.70,metalico\n"
        "Hierro puro,metal_ferroso,7.87,metalico\n"
    )
    df = load_materials(csv)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "material" in df.columns
    assert "familia" in df.columns


def test_load_materials_converts_numeric_columns(tmp_path):
    """Las columnas numéricas deben ser tipo numérico (float o int), no str."""
    csv = tmp_path / "materiales.csv"
    csv.write_text(
        "material,familia,densidad_gcm3,E_GPa,sigma_y_MPa\n"
        "Al,metal_no_ferroso,2.70,69,95\n"
    )
    df = load_materials(csv)
    assert pd.api.types.is_numeric_dtype(df["densidad_gcm3"])
    assert pd.api.types.is_numeric_dtype(df["E_GPa"])
    assert pd.api.types.is_numeric_dtype(df["sigma_y_MPa"])


def test_load_materials_handles_empty_numeric_values(tmp_path):
    """Valores vacíos en columnas numéricas deben convertirse a NaN."""
    csv = tmp_path / "materiales.csv"
    csv.write_text(
        "material,familia,densidad_gcm3,E_GPa\n"
        "Al,metal_no_ferroso,2.70,\n"
    )
    df = load_materials(csv)
    assert pd.isna(df["E_GPa"].iloc[0])


def test_get_material_by_name(tmp_path):
    """get_material_by_name debe devolver una fila por nombre."""
    csv = tmp_path / "materiales.csv"
    csv.write_text(
        "material,familia,densidad_gcm3\n"
        "Aluminio 1100,metal_no_ferroso,2.70\n"
    )
    df = load_materials(csv)
    row = get_material_by_name(df, "Aluminio 1100")
    assert row is not None
    assert row["familia"] == "metal_no_ferroso"


def test_get_material_by_name_not_found(tmp_path):
    """Debe devolver None si el material no existe."""
    csv = tmp_path / "materiales.csv"
    csv.write_text("material,familia,densidad_gcm3\nAl,metal_no_ferroso,2.70\n")
    df = load_materials(csv)
    assert get_material_by_name(df, "Inexistible") is None


def test_list_families(tmp_path):
    """list_families debe devolver lista única y ordenada de familias."""
    csv = tmp_path / "materiales.csv"
    csv.write_text(
        "material,familia,densidad_gcm3\n"
        "Al,metal_no_ferroso,2.70\n"
        "Fe,metal_ferroso,7.87\n"
        "Al2,metal_no_ferroso,2.70\n"
    )
    df = load_materials(csv)
    families = list_families(df)
    assert "metal_no_ferroso" in families
    assert "metal_ferroso" in families
    assert len(families) == 2  # sin duplicados
    # Debe estar ordenado alfabéticamente
    assert families == sorted(families)