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
                 
        st.subheader("Filtros")

        if "Region" in df.columns:
            regiones = st.multiselect("Selecciona región(es)",
                                        options=df["Region"].unique(),
                                        default=df["Region"].unique())
            df = df[df["Region"].isin(regiones)]

       

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
st.subheader("Resumen automático")

resumen_texto = []

if "Ingresos" in kpis:
    ingresos_total = kpis["Ingresos"]["total"]
    ingresos_media = kpis["Ingresos"]["media"]
    resumen_texto.append(f"Los ingresos totales ascienden a {ingresos_total:,.2f}, con una media de {ingresos_media:,.2f} por registro.")

if "Gastos" in kpis:
    gastos_total = kpis["Gastos"]["total"]
    resumen_texto.append(f"Los gastos totales son de {gastos_total:,.2f}.")

if "Ingresos" in kpis and "Gastos" in kpis:
    beneficio = kpis["Ingresos"]["total"] - kpis["Gastos"]["total"]
    margen = (beneficio / kpis["Ingresos"]["total"]) * 100 if kpis["Ingresos"]["total"] > 0 else 0
    resumen_texto.append(f"El beneficio estimado es de {beneficio:,.2f}, lo que representa un margen del {margen:.1f}%.")

if "Region" in df.columns and "Ingresos" in df.columns:
    top_region = df.groupby("Region")["Ingresos"].sum().idxmax()
    resumen_texto.append(f"La región con mayores ingresos es {top_region}.")

if "Tipo Producto" in df.columns and "Ingresos" in df.columns:
    top_producto = df.groupby("Tipo Producto")["Ingresos"].sum().idxmax()
    resumen_texto.append(f"El producto más rentable es {top_producto}.")

for linea in resumen_texto:
    st.write("• " + linea)

st.subheader("Alertas y anomalías")

alertas = []

if "Region" in df.columns:
    for col in ["Ingresos", "Gastos"]:
        if col in df.columns:
            total_anomalias = 0
            
            for region in df["Region"].unique():
                subset = df[df["Region"] == region]
                media = subset[col].mean()
                std = subset[col].std()
                
                if std > 0:
                    limite_superior = media + 2 * std
                    limite_inferior = media - 2 * std
                    anomalias = subset[(subset[col] > limite_superior) | (subset[col] < limite_inferior)]
                    total_anomalias += len(anomalias)
            
            if total_anomalias > 0:
                alertas.append(f"⚠️ Se detectaron {total_anomalias} valores atípicos en '{col}' (comparado dentro de cada región).")

if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.info("✅ No se detectaron anomalías significativas en los datos.")
