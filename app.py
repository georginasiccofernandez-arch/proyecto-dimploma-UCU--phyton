
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Precios Retail UY", layout="wide")

st.title("Comparador de Precios Inteligente")
st.markdown("Encuentra las opciones más eficientes y ahorra en tu compra comparando las tarifas del mercado.")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/precios_supermercados_uy_limpio.csv")

df = load_data()

st.sidebar.header("Filtros de Búsqueda")
st.sidebar.markdown("Ajusta las opciones para encontrar el mejor precio.")

trimestres = st.sidebar.multiselect("Trimestre", options=df['Trimestre'].unique(), default=df['Trimestre'].unique())
grupos = st.sidebar.multiselect("🏷Categoría de Producto", options=df['Grupo'].unique(), default=df['Grupo'].unique())
supers = st.sidebar.multiselect("Supermercado", options=df['Super'].unique(), default=df['Super'].unique())

min_p, max_p = float(df['Precio'].min()), float(df['Precio'].max())
rango_precio = st.sidebar.slider(" Rango de Precio ($)", min_value=min_p, max_value=max_p, value=(min_p, max_p))

df_filtrado = df[
    (df['Trimestre'].isin(trimestres)) &
    (df['Grupo'].isin(grupos)) &
    (df['Super'].isin(supers)) &
    (df['Precio'] >= rango_precio[0]) &
    (df['Precio'] <= rango_precio[1])
    ]

st.markdown("### Oportunidades de Ahorro")

if not df_filtrado.empty:
    col1, col2, col3 = st.columns(3)


    super_mas_barato = df_filtrado.groupby('Super')['Precio'].mean().idxmin()
    precio_promedio = df_filtrado['Precio'].mean()
    precio_minimo = df_filtrado['Precio'].min()

    col1.metric("Supermercado más Económico (Promedio)", super_mas_barato)
    col2.metric("Precio Promedio del Mercado", f"${precio_promedio:.2f}")
    col3.metric("Precio Mínimo Encontrado", f"${precio_minimo:.2f}")

    st.divider()


    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("**Comparativa de Precios por Cadena**")

        df_agrupado = df_filtrado.groupby('Super', as_index=False)['Precio'].mean().sort_values(by='Precio')
        fig_bar = px.bar(
            df_agrupado,
            x='Super',
            y='Precio',
            color='Super',
            text_auto='.2f',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(xaxis_title="Supermercado", yaxis_title="Precio Promedio ($)", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_graf2:
        st.markdown("**Rango de Precios por Categoría**")

        fig_box = px.box(
            df_filtrado,
            x='Grupo',
            y='Precio',
            color='Grupo',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_box.update_layout(xaxis_title="Categoría de Producto", yaxis_title="Precio ($)", showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)


    st.markdown("### Detalle de Productos")
    st.dataframe(df_filtrado[['Super', 'Grupo', 'Producto', 'Precio', 'Trimestre']].sort_values(by='Precio').head(50),
                 use_container_width=True)

else:
    st.warning("No hay productos que coincidan con estos filtros. Intenta ampliar la búsqueda en el panel lateral.")