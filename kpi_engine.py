import pandas as pd

def calcular_kpis(df):
    kpis = {}
    
    # Detectar columnas numéricas
    numericas = df.select_dtypes(include="number").columns.tolist()
    
    for col in numericas:
        kpis[col] = {
            "total": df[col].sum(),
            "media": round(df[col].mean(), 2),
            "maximo": df[col].max(),
            "minimo": df[col].min()
        }
    
    return kpis

def mostrar_kpis(kpis):
    for col, valores in kpis.items():
        print(f"\n📊 {col}")
        for k, v in valores.items():
            print(f"  {k}: {v}")
