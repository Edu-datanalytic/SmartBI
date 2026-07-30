import pandas as pd

def cargar_datos(ruta):
    if ruta.endswith(".csv"):
        df = pd.read_csv(ruta)
    elif ruta.endswith(".xlsx"):
        df = pd.read_excel(ruta)
    else:
        raise ValueError("Formato no soportado")
    return df

def limpiar_datos(df):
    df = df.fillna("")
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()
    return df

def resumen(df):
    print(f"Filas: {len(df)}")
    print(f"Columnas: {list(df.columns)}")
    return df.describe()
