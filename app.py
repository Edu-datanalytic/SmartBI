import streamlit as st
import pandas as pd
from kpi_engine import calcular_kpis
def fmt(x):
      return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"
st.set_page_config(
    page_title="SmartBI",
    page_icon="📊",
    layout="wide"
)
def detalle_anomalias(df, col, n=5):
    filas = []
    for (region, producto), subset in df.groupby(["Region", "Tipo Producto"]):
        if len(subset) >= 3:
            media = subset[col].mean()
            std = subset[col].std()
            if std > 0:
                for valor in subset[col]:
                    z = (valor - media) / std
                    if abs(z) > 2.5:
                        filas.append((abs(z), region, producto, valor, media))
    lineas = []
    for z, region, producto, valor, media in sorted(filas, reverse=True)[:n]:
        lineas.append(
            f"   • {region} / {producto}: {col} de {fmt(valor)} frente a {fmt(media)} habitual "
            f"({f'{z:.1f}'.replace('.', ',')} desviaciones estándar)."
        )
    return lineas
st.title("📊 SmartBI")
st.write("Análisis automático de datos para PYMEs")

archivo = st.file_uploader(
    "Sube un archivo CSV o Excel",
    type=["csv", "xlsx"]
)

if archivo is None:
    st.info("👆 Sube un archivo CSV o Excel para empezar.")
    st.stop()
    
if archivo is not None:
    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado correctamente")

        st.subheader("Vista previa")
        st.dataframe(df.dropna(axis=1, how="all").style.format({c: fmt for c in ["Ingresos", "Gastos"] if c in df.columns}), width="stretch")
                 
        st.subheader("Filtros")

        if "Region" in df.columns:
            regiones = st.multiselect("Selecciona región(es)",
                                        options=df["Region"].unique(),
                                        default=df["Region"].unique())
            df = df[df["Region"].isin(regiones)]

       

        st.subheader("KPIs automáticos")
        kpis = calcular_kpis(df)
        kpis = {k: v for k, v in kpis.items() if v["total"] != 0}

          

        columnas = st.columns(len(kpis))

        for i, (col, valores) in enumerate(kpis.items()):
            columnas[i].metric(
                label=f"{col} (Total)",
                value=f"{valores['total']:,.0f}".replace(",",".") + " €"
            )

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
import plotly.express as px


st.subheader("Ingresos por región")
if "Region" in df.columns and "Ingresos" in df.columns:
    resumen_region = df.groupby("Region")["Ingresos"].sum().nlargest(10).reset_index()

    fig1 = px.bar(
        resumen_region,
        x="Region",
        y="Ingresos",
        title="Top 10 regiones por ingresos",
        labels={"Region": "Región", "Ingresos": "Ingresos (€)"}
    )

    fig1.update_yaxes(
    tickmode="array",
    tickvals=[0, 200_000_000, 400_000_000, 600_000_000,
              800_000_000, 1_000_000_000, 1_200_000_000],
    ticktext=["0", "200 M€", "400 M€", "600 M€",
              "800 M€", "1.000 M€", "1.200 M€"]
)
    fig1.update_traces(
        hovertemplate="Región: %{x}<br>Ingresos: %{y:,.2f} €<extra></extra>"
    )

    st.plotly_chart(fig1, width="stretch")


st.subheader("Ingresos por producto")
if "Tipo Producto" in df.columns and "Ingresos" in df.columns:
    resumen_producto = df.groupby("Tipo Producto")["Ingresos"].sum().reset_index()

    fig2 = px.bar(
        resumen_producto,
        x="Tipo Producto",
        y="Ingresos",
        title="Ingresos totales por tipo de producto",
        labels={
            "Tipo Producto": "Tipo de producto",
            "Ingresos": "Ingresos (€)"
        }
    )

    
fig2.update_yaxes(
    tickmode="array",
    tickvals=[0, 200_000_000, 400_000_000, 600_000_000,
              800_000_000, 1_000_000_000, 1_200_000_000],
    ticktext=["0", "200 M€", "400 M€", "600 M€",
              "800 M€", "1.000 M€", "1.200 M€"]
)

fig2.update_traces(    
        hovertemplate="Producto: %{x}<br>Ingresos: %{y:,.2f} €<extra></extra>"
    )

st.plotly_chart(fig2, width="stretch")    


st.subheader("Resumen automático")


resumen_texto = []

if "Ingresos" in kpis:
    ingresos_total = kpis["Ingresos"]["total"]
    ingresos_media = kpis["Ingresos"]["media"]
    resumen_texto.append(f"Los ingresos totales ascienden a {fmt(ingresos_total)}, con una media de {fmt(ingresos_media)} por registro.")

if "Gastos" in kpis:
    gastos_total = kpis["Gastos"]["total"]
    resumen_texto.append(f"Los gastos totales son de {fmt(gastos_total)}.")

if "Ingresos" in kpis and "Gastos" in kpis:
    beneficio = kpis["Ingresos"]["total"] - kpis["Gastos"]["total"]
    margen = (beneficio / kpis["Ingresos"]["total"]) * 100 if kpis["Ingresos"]["total"] > 0 else 0
    resumen_texto.append(f"El beneficio estimado es de {fmt(beneficio)}, lo que representa un margen del {f'{margen:.1f}'.replace('.', ',')}%.")

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

if "Region" in df.columns and "Tipo Producto" in df.columns:
    for col in ["Ingresos", "Gastos"]:
        if col in df.columns:
            total_anomalias = 0
            
            grupos = df.groupby(["Region", "Tipo Producto"])
            
            for (region, producto), subset in grupos:
                if len(subset) >= 3:
                    media = subset[col].mean()
                    std = subset[col].std()
                    
                    if std > 0:
                        limite_superior = media + 2.5 * std
                        limite_inferior = media - 2.5 * std
                        anomalias = subset[(subset[col] > limite_superior) | (subset[col] < limite_inferior)]
                        total_anomalias += len(anomalias)
            
            if total_anomalias > 0:
                alertas.append(f"⚠️ Se detectaron {total_anomalias} valores atípicos en '{col}' (comparado dentro de cada región y producto).")
                alertas.extend(detalle_anomalias(df, col))
if not ("Region" in df.columns and "Tipo Producto" in df.columns):
    col_fecha = next((c for c in df.columns if str(c).lower() in ["date", "fecha"]), None)
    col_valor = next((c for c in df.columns if str(c).lower() in ["sales", "ventas", "ingresos"]), None)

    if col_valor is not None:
        serie = df.copy()
        serie[col_valor] = pd.to_numeric(serie[col_valor], errors="coerce")
        serie = serie.dropna(subset=[col_valor])

        if len(serie) >= 10:
            media = serie[col_valor].mean()
            std = serie[col_valor].std()

            if std > 0:
                serie["z"] = (serie[col_valor] - media) / std
                atipicos = serie[serie["z"].abs() > 2.5]
                if len(atipicos) > 0:               
                    atipicos = atipicos.reindex(atipicos["z"].abs().sort_values(ascending=False).index)
                    mayor = atipicos.iloc[0]
                    fecha_mayor = mayor[col_fecha] if col_fecha else "sin fecha"
                    alertas.append(
                        f"📊 Resumen: se detectaron {len(atipicos)} días atípicos sobre {len(serie)}. "
                        f"El más extremo es {fecha_mayor}, con ventas de {mayor[col_valor]:,.2f}."
                    )

                for _, fila in atipicos.iterrows():
                    fecha = fila[col_fecha] if col_fecha else "sin fecha"
                    tipo = "por encima" if fila["z"] > 0 else "por debajo"
                    alertas.append(
                        f"⚠️ {fecha}: ventas de {fila[col_valor]:,.2f}, "
                        f"{tipo} de lo habitual (media {fmt(media)}). "
                        f"Se aleja {abs(fila['z']):.1f} desviaciones estándar. "
                        f"Conviene revisar si es un dato correcto."
                    )
            if col_fecha:       
                    serie[col_fecha] = pd.to_datetime(serie[col_fecha], errors="coerce")
                    atipicos = serie[serie["z"].abs() > 2.5]
                    fig_anom = px.line(
                        serie, x=col_fecha, y=col_valor,
                        title="Ventas por día y días atípicos"
                    )
                    fig_anom.add_scatter(
                        x=atipicos[col_fecha], y=atipicos[col_valor],
                        mode="markers", name="Anomalías",
                        marker=dict(color="red", size=10)
                    )
                    st.plotly_chart(fig_anom, width="stretch")                 
if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.info("✅ No se detectaron anomalías significativas en los datos.")

from fpdf import FPDF
st.subheader("Exportar informe")

if st.button("Generar informe PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Informe SmartBI", ln=True)
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 10, "Resumen ejecutivo:" if resumen_texto else "", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for linea in resumen_texto:
        linea_limpia = linea.replace("€", "EUR").encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, linea_limpia, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Alertas y anomalias:", ln=True)
    pdf.set_font("Arial", "", 10)
    if alertas:
        for alerta in alertas:
            alerta_limpia = alerta.replace("€", "EUR").encode("latin-1", "ignore").decode("latin-1")
            pdf.multi_cell(0, 8, alerta_limpia, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.multi_cell(0, 8, "No se detectaron anomalias significativas.", new_x="LMARGIN", new_y="NEXT")
    pdf.output("informe_smartbi.pdf")
    
    with open("informe_smartbi.pdf", "rb") as f:
        st.download_button(
            label="Descargar PDF",
            data=f,
            file_name="informe_smartbi.pdf",
            mime="application/pdf"
        )
