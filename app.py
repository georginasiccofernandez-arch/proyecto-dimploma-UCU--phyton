
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ahorro Inteligente - Retail UY", layout="wide")

st.title("Comparador de Precios Inteligente")
st.markdown("Encuentra las opciones más eficientes y ahorra en tu compra comparando las tarifas del mercado.")


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/precios_supermercados_uy_limpio.csv")


df = load_data()

tab1, tab2 = st.tabs(["Análisis de Mercado", "Simulador de Canasta Básica"])

with tab1:
    st.sidebar.header("Filtros de Búsqueda")
    st.sidebar.markdown("Ajusta las opciones para el Análisis de Mercado.")

    busqueda = st.sidebar.text_input("Buscar Producto (Ej. yerba, arroz, aceite)...", "").lower()

    trimestres = st.sidebar.multiselect("Trimestre", options=df['Trimestre'].unique(), default=df['Trimestre'].unique())
    grupos = st.sidebar.multiselect("Categoría de Producto", options=df['Grupo'].unique(), default=df['Grupo'].unique())
    supers = st.sidebar.multiselect("Supermercado", options=df['Super'].unique(), default=df['Super'].unique())

    min_p, max_p = float(df['Precio'].min()), float(df['Precio'].max())
    rango_precio = st.sidebar.slider("Rango de Precio ($)", min_value=min_p, max_value=max_p, value=(min_p, max_p))

    df_filtrado = df[
        (df['Trimestre'].isin(trimestres)) &
        (df['Grupo'].isin(grupos)) &
        (df['Super'].isin(supers)) &
        (df['Precio'] >= rango_precio[0]) &
        (df['Precio'] <= rango_precio[1])
        ]

    if busqueda:
        df_filtrado = df_filtrado[df_filtrado['Producto'].str.lower().str.contains(busqueda)]

    st.markdown("### Oportunidades de Ahorro")

    if not df_filtrado.empty:
        col1, col2, col3 = st.columns(3)

        super_mas_barato = df_filtrado.groupby('Super')['Precio'].mean().idxmin()
        precio_promedio = df_filtrado['Precio'].mean()
        precio_minimo = df_filtrado['Precio'].min()

        col1.metric("Supermercado más Económico", super_mas_barato)
        col2.metric("Precio Promedio del Mercado", f"${precio_promedio:.2f}")
        col3.metric("Precio Mínimo Encontrado", f"${precio_minimo:.2f}")

        st.divider()

        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            st.markdown("**Comparativa de Tarifas por Cadena**")
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
            fig_box.update_layout(xaxis_title="Categoría", yaxis_title="Precio ($)", showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("### Detalle de Productos")
        st.dataframe(
            df_filtrado[['Super', 'Grupo', 'Producto', 'Precio', 'Trimestre']].sort_values(by='Precio').head(50),
            use_container_width=True)

    else:
        st.warning("No hay productos que coincidan con la búsqueda. Intenta probar con otra palabra clave.")

with tab2:
    st.markdown("### Arma tu propia Canasta y descubre dónde comprarla")
    st.markdown(
        "Selecciona los productos específicos que llevas en tu compra habitual. El simulador calculará el costo total del ticket en cada supermercado, asumiendo una unidad por producto.")

    productos_disponibles = sorted(df['Producto'].unique())
    canasta_seleccionada = st.multiselect(
        "Selecciona tus productos:",
        options=productos_disponibles,
        placeholder="Ej. elige leche, pan, huevos..."
    )

    if canasta_seleccionada:
        df_canasta = df[df['Producto'].isin(canasta_seleccionada)]

        ticket_por_super = df_canasta.groupby(['Super', 'Producto'])['Precio'].mean().reset_index()
        ticket_total = ticket_por_super.groupby('Super')['Precio'].sum().reset_index()
        ticket_total = ticket_total.sort_values(by='Precio')

        st.divider()

        ganador = ticket_total.iloc[0]
        st.success(
            f"**El ticket más barato para esta canasta está en {ganador['Super']}** por un total aproximado de **${ganador['Precio']:.2f}**")

        fig_ticket = px.bar(
            ticket_total,
            x='Super',
            y='Precio',
            color='Super',
            text_auto='.2f',
            title="Costo Total de tu Canasta por Supermercado",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_ticket.update_layout(xaxis_title="", yaxis_title="Costo Total ($)", showlegend=False)
        st.plotly_chart(fig_ticket, use_container_width=True)

        st.markdown("**Desglose estimado por cadena:**")
        st.dataframe(ticket_total.rename(columns={'Precio': 'Costo Total ($)'}).set_index('Super').T)
    else:
        st.info("Selecciona al menos un producto arriba para comenzar la simulación de tu ticket.")