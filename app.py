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
import plotly.express as px

st.subheader("Ingresos por región")
if "Region" in df.columns and "Ingresos" in df.columns:
    resumen_region = df.groupby("Region")["Ingresos"].sum().reset_index()
    fig1 = px.bar(resumen_region, x="Region", y="Ingresos", 
                   title="Ingresos totales por región")
    st.plotly_chart(fig1, use_container_width=True)

st.subheader("Ingresos por producto")
if "Tipo Producto" in df.columns and "Ingresos" in df.columns:
    resumen_producto = df.groupby("Tipo Producto")["Ingresos"].sum().reset_index()
    fig2 = px.bar(resumen_producto, x="Tipo Producto", y="Ingresos",
                   title="Ingresos totales por tipo de producto")
    st.plotly_chart(fig2, use_container_width=True)
