"""Ashby Edu — App web de selección de materiales (Streamlit).

Ejecutar:
    streamlit run src/ashby_edu/app.py
"""
from __future__ import annotations

import streamlit as st

from ashby_edu.data_loader import load_materials, list_families
from ashby_edu.indices import AVAILABLE_INDICES, compute_index
from ashby_edu.ashby_chart import create_ashby_chart
from ashby_edu.cases import load_cases, list_case_names

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Ashby Edu — Selección de Materiales",
    page_icon="🔬",
    layout="wide",
)


# ── Cargar datos (cache) ────────────────────────────────────────────────────
@st.cache_data
def get_data():
    """Carga el CSV de materiales y calcula todos los índices."""
    df = load_materials()
    df = compute_index(df, "all")
    return df


@st.cache_data
def get_cases():
    """Carga los casos industriales desde YAML."""
    return load_cases()


# ── Datos ────────────────────────────────────────────────────────────────────
df = get_data()
cases = get_cases()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🔬 Ashby Edu")
st.sidebar.caption("Selección de materiales — UTEQ Ing. Industrial")
st.sidebar.divider()
st.sidebar.info(
    f"**{len(df)} materiales** cargados\n"
    f"**{len(cases)} casos** industriales\n"
    f"**{len(AVAILABLE_INDICES)}** índices de desempeño"
)


# ── Pestañas ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Carta de Ashby",
    "🏭 Casos Industriales",
    "📋 Base de Datos",
])


# ── Tab 1: Carta de Ashby (modo libre) ──────────────────────────────────────
with tab1:
    st.header("Carta de Ashby — Modo Libre")

    col1, col2 = st.columns(2)
    with col1:
        # Ejes disponibles: propiedades físicas + índices calculados
        base_props = [
            "densidad_gcm3", "E_GPa", "sigma_y_MPa", "sigma_UTS_MPa",
            "elongacion_pct", "dureza_HB", "k_WmK", "alfa_1e-6C",
            "T_fusion_C", "costo_USD_kg", "energia_embebida_MJkg",
            "huella_CO2_kgCO2kg",
        ]
        index_cols = [f"M_{name}" for name in AVAILABLE_INDICES]
        x_options = base_props + index_cols
        x_default = "densidad_gcm3" if "densidad_gcm3" in df.columns else x_options[0]
        x_col = st.selectbox(
            "Eje X",
            x_options,
            index=x_options.index(x_default) if x_default in x_options else 0,
            format_func=lambda c: AVAILABLE_INDICES[c[2:]]["formula"]
            if c.startswith("M_") and c[2:] in AVAILABLE_INDICES
            else c,
        )
    with col2:
        y_default = "E_GPa" if "E_GPa" in df.columns else x_options[0]
        y_col = st.selectbox(
            "Eje Y",
            x_options,
            index=x_options.index(y_default) if y_default in x_options else 0,
            format_func=lambda c: AVAILABLE_INDICES[c[2:]]["formula"]
            if c.startswith("M_") and c[2:] in AVAILABLE_INDICES
            else c,
        )

    # Filtro de familias
    all_families = list_families(df)
    selected_families = st.multiselect(
        "Familias a mostrar",
        all_families,
        default=all_families,
    )
    df_filtered = (
        df[df["familia"].isin(selected_families)]
        if selected_families
        else df
    )

    # ── Línea de índice de desempeño ──
    st.subheader("Índice de desempeño")
    show_index_line = st.checkbox("Mostrar línea de índice", value=False)
    if show_index_line:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            slope = st.slider("Pendiente (exponente p)", -3.0, 3.0, 1.0, 0.1)
        with col_s2:
            intercept = st.slider(
                "Constante C (y = C · x^p)", 0.01, 1000.0, 10.0, 0.1
            )
    else:
        slope, intercept = None, None

    # ── Selección de candidatos ──
    st.subheader("Mis materiales candidatos")
    all_materials = df["material"].tolist()
    candidates = st.multiselect(
        "Selecciona materiales para superponer",
        all_materials,
    )
    df_candidates = (
        df[df["material"].isin(candidates)] if candidates else None
    )

    # ── Gráfica ──
    fig = create_ashby_chart(
        df_filtered,
        x_col=x_col,
        y_col=y_col,
        df_candidates=df_candidates,
        index_line_slope=slope,
        index_line_intercept=intercept,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Comparación de candidatos ──
    if df_candidates is not None and not df_candidates.empty:
        st.subheader("Comparación de candidatos")
        compare_cols = [
            "material", "familia", "densidad_gcm3", "E_GPa",
            "sigma_y_MPa", "sigma_UTS_MPa", "costo_USD_kg",
        ]
        available_cols = [c for c in compare_cols if c in df_candidates.columns]
        st.dataframe(
            df_candidates[available_cols].sort_values("densidad_gcm3"),
            use_container_width=True,
            hide_index=True,
        )

    # ── Exportar ──
    st.subheader("Exportar")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        try:
            png_bytes = fig.to_image(format="png", scale=2)
            st.download_button(
                label="📥 Descargar gráfica (PNG)",
                data=png_bytes,
                file_name="carta_ashby.png",
                mime="image/png",
            )
        except Exception:
            st.info("Instala kaleido para exportar PNG: pip install kaleido")

    with col_exp2:
        if df_candidates is not None and not df_candidates.empty:
            csv_data = df_candidates.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📊 Descargar candidatos (CSV)",
                data=csv_data,
                file_name="materiales_seleccionados.csv",
                mime="text/csv",
            )
        else:
            st.caption("Selecciona candidatos para exportar CSV")


# ── Tab 2: Casos Industriales (modo guiado) ────────────────────────────────
with tab2:
    st.header("Casos Industriales — Modo Guiado")

    case_names = list_case_names(cases)
    selected_name = st.selectbox("Selecciona un caso", case_names)
    case = next(c for c in cases if c["nombre"] == selected_name)

    st.subheader(case["nombre"])
    if case.get("es_rector"):
        st.badge("⭐ Caso rector")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write(f"**Sector:** {case.get('sector', 'N/A')}")
        st.write(f"**Proceso:** {case.get('proceso', 'N/A')}")
    with col_c2:
        st.write(f"**Volumen:** {case.get('volumen', 'N/A')}")
        st.write(f"**Función:** {case.get('funcion', 'N/A')}")

    st.write("**Restricciones clave:**")
    for r in case.get("restricciones", []):
        st.write(f"  • {r}")

    st.write("**Normas relevantes:**")
    for n in case.get("normas", []):
        st.write(f"  • {n}")

    st.write("**Materiales candidatos:**")
    cands = case.get("candidatos", [])
    st.write(", ".join(cands) if cands else "N/A")

    # Carta precargada
    cfg = case.get("ashby_config", {})
    if cfg:
        st.divider()
        st.write("**Carta de Ashby precargada para este caso:**")
        # Filtrar BD para mostrar solo las familias relevantes
        fig = create_ashby_chart(
            df,
            x_col=cfg.get("x_col", "densidad_gcm3"),
            y_col=cfg.get("y_col", "sigma_y_MPa"),
            index_line_slope=cfg.get("index_line_slope"),
            index_line_intercept=cfg.get("index_line_intercept"),
            title=f"Carta de Ashby — {case['nombre']}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "Este caso no tiene configuración precargada. Usa la pestaña "
            "Carta de Ashby para explorar libremente."
        )


# ── Tab 3: Explorar Base de Datos ────────────────────────────────────────────
with tab3:
    st.header("Base de Datos de Materiales")
    st.write(f"**{len(df)} materiales** · **{len(df.columns)} propiedades**")

    # Buscador
    search = st.text_input("Buscar material por nombre")
    if search:
        df_show = df[df["material"].str.contains(search, case=False)]
    else:
        df_show = df

    # Selector de columnas para mostrar
    st.subheader("Columnas a mostrar")
    all_cols = df.columns.tolist()
    default_cols = [
        c for c in [
            "material", "familia", "densidad_gcm3", "E_GPa",
            "sigma_y_MPa", "sigma_UTS_MPa", "costo_USD_kg",
        ]
        if c in all_cols
    ]
    show_cols = st.multiselect(
        "Selecciona columnas", all_cols, default=default_cols
    )
    st.dataframe(df_show[show_cols] if show_cols else df_show, use_container_width=True, hide_index=True)