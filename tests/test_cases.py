"""Tests para ashby_edu.cases."""
from __future__ import annotations

import pytest
import yaml

from ashby_edu.cases import load_cases, get_case_by_id, list_case_names


# Campos obligatorios de cada caso
REQUIRED_FIELDS = [
    "id",
    "nombre",
    "sector",
    "funcion",
    "proceso",
    "volumen",
    "restricciones",
    "normas",
    "candidatos",
    "ashby_config",
    "es_rector",
]

ASHBY_CONFIG_FIELDS = ["x_col", "y_col", "index_line_slope", "index_line_intercept"]


def _write_yaml(tmp_path, data):
    """Escribe una lista de casos a un YAML temporal y devuelve la ruta."""
    p = tmp_path / "casos.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _sample_cases():
    """Casos mínimos para pruebas unitarias."""
    return [
        {
            "id": "caso-a",
            "nombre": "Caso A",
            "sector": "Sector A",
            "funcion": "Función A",
            "proceso": "Proceso A",
            "volumen": "1000 uds",
            "restricciones": ["r1", "r2"],
            "normas": ["N1", "N2"],
            "candidatos": ["Mat1", "Mat2"],
            "ashby_config": {
                "x_col": "densidad_gcm3",
                "y_col": "sigma_y_MPa",
                "index_line_slope": 1.0,
                "index_line_intercept": 50.0,
            },
            "es_rector": True,
        },
        {
            "id": "caso-b",
            "nombre": "Caso B",
            "sector": "Sector B",
            "funcion": "Función B",
            "proceso": "Proceso B",
            "volumen": "2000 uds",
            "restricciones": ["r3"],
            "normas": ["N3"],
            "candidatos": ["Mat3"],
            "ashby_config": {
                "x_col": "E_GPa",
                "y_col": "sigma_UTS_MPa",
                "index_line_slope": 2.0,
                "index_line_intercept": 10.0,
            },
            "es_rector": False,
        },
    ]


# ----- load_cases -----------------------------------------------------------

def test_load_cases_returns_list_of_dicts(tmp_path):
    """load_cases debe devolver una lista de dicts."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    assert isinstance(cases, list)
    assert len(cases) == 2
    assert all(isinstance(c, dict) for c in cases)


def test_load_cases_each_has_required_fields(tmp_path):
    """Cada caso debe tener todos los campos obligatorios."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    for c in cases:
        for f in REQUIRED_FIELDS:
            assert f in c, f"Campo faltante: {f} en caso {c.get('id')}"


def test_load_cases_ashby_config_fields(tmp_path):
    """ashby_config debe tener x_col, y_col, slope e intercept."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    for c in cases:
        cfg = c["ashby_config"]
        for f in ASHBY_CONFIG_FIELDS:
            assert f in cfg, f"ashby_config falta {f}"


def test_load_cases_restricciones_is_list(tmp_path):
    """restricciones, normas y candidatos deben ser listas."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    for c in cases:
        assert isinstance(c["restricciones"], list)
        assert isinstance(c["normas"], list)
        assert isinstance(c["candidatos"], list)


def test_load_cases_es_rector_is_bool(tmp_path):
    """es_rector debe ser bool."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    for c in cases:
        assert isinstance(c["es_rector"], bool)


def test_load_cases_empty_yaml(tmp_path):
    """Un YAML vacío (lista vacía) debe devolver lista vacía."""
    path = _write_yaml(tmp_path, [])
    assert load_cases(path) == []


# ----- get_case_by_id -------------------------------------------------------

def test_get_case_by_id_found(tmp_path):
    """get_case_by_id devuelve el dict del caso solicitado."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    c = get_case_by_id(cases, "caso-a")
    assert c is not None
    assert c["nombre"] == "Caso A"


def test_get_case_by_id_not_found(tmp_path):
    """get_case_by_id devuelve None si el id no existe."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    assert get_case_by_id(cases, "inexistente") is None


def test_get_case_by_id_empty_cases(tmp_path):
    """get_case_by_id sobre lista vacía devuelve None."""
    assert get_case_by_id([], "x") is None


# ----- list_case_names ------------------------------------------------------

def test_list_case_names(tmp_path):
    """list_case_names devuelve los nombres en el mismo orden."""
    path = _write_yaml(tmp_path, _sample_cases())
    cases = load_cases(path)
    names = list_case_names(cases)
    assert names == ["Caso A", "Caso B"]


def test_list_case_names_empty(tmp_path):
    """list_case_names sobre lista vacía devuelve []."""
    assert list_case_names([]) == []


# ----- Integración con data/casos.yaml real --------------------------------

def test_default_path_loads_10_cases():
    """load_cases() sin argumentos carga data/casos.yaml con exactamente 10 casos."""
    cases = load_cases()
    assert len(cases) == 10


def test_default_cases_have_required_fields():
    """Todos los casos reales tienen los campos obligatorios."""
    cases = load_cases()
    for c in cases:
        for f in REQUIRED_FIELDS:
            assert f in c, f"Campo faltante: {f} en {c.get('id')}"
        for f in ASHBY_CONFIG_FIELDS:
            assert f in c["ashby_config"], f"ashby_config falta {f} en {c.get('id')}"


def test_default_cases_ids():
    """Los IDs de los 10 casos reales deben ser los esperados."""
    expected_ids = [
        "carcasa-taladro",
        "botella-bebida-carbonatada",
        "tarima-industrial-pallet",
        "tuberia-proceso-alimentos",
        "engrane-transmision",
        "gabinete-electrico-nema4",
        "contenedor-residuos-industriales",
        "rodillo-transportador",
        "inserto-herramienta-corte",
        "carcasa-electrodomestico-licuadora",
    ]
    cases = load_cases()
    ids = [c["id"] for c in cases]
    assert ids == expected_ids


def test_default_has_exactly_one_rector():
    """Debe haber exactamente un caso rector (carcasa-taladro)."""
    cases = load_cases()
    rectores = [c for c in cases if c["es_rector"] is True]
    assert len(rectores) == 1
    assert rectores[0]["id"] == "carcasa-taladro"


def test_default_carcasa_taladro_config():
    """El caso rector tiene ashby_config con slope=1.0 e intercept=50.0."""
    cases = load_cases()
    c = get_case_by_id(cases, "carcasa-taladro")
    assert c is not None
    assert c["ashby_config"]["index_line_slope"] == 1.0
    assert c["ashby_config"]["index_line_intercept"] == 50.0
    assert c["ashby_config"]["x_col"] == "densidad_gcm3"
    assert c["ashby_config"]["y_col"] == "sigma_y_MPa"


def test_default_list_case_names_count():
    """list_case_names sobre los casos reales devuelve 10 nombres."""
    cases = load_cases()
    assert len(list_case_names(cases)) == 10