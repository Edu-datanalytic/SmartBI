import streamlit as st
import pandas as pd
from kpi_engine import calcular_kpis

st.set_page_config(
    page_title="SmartBI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SmartBI")
st.write("Análisis automático de datos para PYMEs")

archivo = st.file_uploader(
    "Sube un archivo CSV o Excel",
    type=["csv", "xlsx"]
)

if archivo is not None:

    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado correctamente")

        st.subheader("Vista previa")
        st.dataframe(df, use_container_width=True)

        st.subheader("KPIs automáticos")

        kpis = calcular_kpis(df)

        columnas = st.columns(len(kpis))

        for i, (col, valores) in enumerate(kpis.items()):
            columnas[i].metric(
                label=f"{col} (Total)",
                value=round(valores["total"], 2)
            )

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")