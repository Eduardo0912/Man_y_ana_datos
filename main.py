
#Primero ejecutar los siguientes comandos en la consola
#pip install streamlit pandas plotly openai
#streamlit run main.py 


import streamlit as st
import pandas as pd
import plotly.express as px
import openai

# Configuración de la página
st.set_page_config(page_title="Análisis de Indicadores Financieros", layout="wide")

# Título del dashboard
st.title("Análisis de Indicadores Financieros")

# Definir paleta de colores spooky
spooky_colors = ['#853174', '#ffa000', '#9451bb', '#2E3718', '#ff7043', '#ffab00', '#ff1744', '#a1887f', '#ff3d00', '#ff6d00']


# Cargar datos
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Eduardo0912/Man_y_ana_datos/refs/heads/main/Datos_proyecto_limpio.csv"
    df = pd.read_csv(url)


    # Calcular Financial_Expenses_Coverage_Ratio
    df['Financial_Expenses_Coverage_Ratio'] = df['Total_Revenue'] / df['Financial_Expenses']

    # Convertir Equity y Total_Revenue a millones de dólares
    df['Equity_Millions'] = df['Equity'] / 1_000_000
    df['Total_Revenue_Millions'] = df['Total_Revenue'] / 1_000_000

    return df

df = load_data()

# Sidebar para filtros
st.sidebar.header("Filtros")
industry = st.sidebar.multiselect("Seleccionar Industria", options=df['Industry'].unique())
country = st.sidebar.multiselect("Seleccionar País", options=df['Country'].unique())
company_size = st.sidebar.multiselect("Seleccionar Tamaño de Empresa", options=df['Company_Size'].unique())

# Aplicar filtros
def filter_dataframe(df, industry, country, company_size):
    filtered_df = df.copy()
    if industry:
        filtered_df = filtered_df[filtered_df['Industry'].isin(industry)]
    if country:
        filtered_df = filtered_df[filtered_df['Country'].isin(country)]
    if company_size:
        filtered_df = filtered_df[filtered_df['Company_Size'].isin(company_size)]
    return filtered_df

filtered_df = filter_dataframe(df, industry, country, company_size)

# Función para crear tablas top 3
def create_top_3_table(df, column, title):
    st.subheader(title)
    top_3 = df.nlargest(3, column)[['Company_ID', column, 'Industry', 'Country']]
    st.table(top_3)

# Función para crear gráficos de barras
def create_bar_chart(df, column, title):
    st.subheader(title)
    fig = px.bar(df.sort_values(column, ascending=False), 
                 x='Company_ID', y=column, 
                 color='Company_Size',
                 color_discrete_sequence=spooky_colors,
                 title=title, 
                 labels={column: title, 'Company_ID': 'Empresa'})
    fig.update_layout(legend_title_text='Tamaño de Empresa')
    st.plotly_chart(fig)

# Función para crear gráficos de pastel
def create_pie_chart(df, values, names, title):
    st.subheader(title)
    fig = px.pie(df, values=values, names=names, title=title,
                 color_discrete_sequence=spooky_colors)
    st.plotly_chart(fig)

# Mostrar información sobre los filtros aplicados
st.write("Filtros aplicados:")
st.write(f"Industria: {', '.join(industry) if industry else 'Todas'}")
st.write(f"País: {', '.join(country) if country else 'Todos'}")
st.write(f"Tamaño de Empresa: {', '.join(company_size) if company_size else 'Todos'}")

# Layout del dashboard
col1, col2 = st.columns(2)

with col1:
    create_top_3_table(filtered_df, 'Total_Revenue_Millions', "Top 3 empresas por ingresos totales (Millones USD)")

with col2:
    create_top_3_table(filtered_df, 'Equity_Millions', "Top 3 empresas por patrimonio (Millones USD)")

create_bar_chart(filtered_df, 'Current_Ratio', "Ratio de liquidez")
create_bar_chart(filtered_df, 'Debt_to_Equity_Ratio', "Ratio deuda a patrimonio")
create_bar_chart(filtered_df, 'Financial_Expenses_Coverage_Ratio', "Cobertura de Gastos Financieros")

# Nuevos gráficos de pastel
col3, col4 = st.columns(2)

with col3:
    equity_by_industry = filtered_df.groupby('Industry')['Equity_Millions'].sum().reset_index()
    create_pie_chart(equity_by_industry, 'Equity_Millions', 'Industry', "Porcentaje de Equity por Industria")

with col4:
    revenue_by_industry = filtered_df.groupby('Industry')['Total_Revenue_Millions'].sum().reset_index()
    create_pie_chart(revenue_by_industry, 'Total_Revenue_Millions', 'Industry', "Porcentaje de Ingresos Totales por Industria")

# Mostrar el número de empresas después de aplicar los filtros
st.write(f"Número de empresas mostradas: {len(filtered_df)}")




st.header("Consulta a tu asistente de IA")

# Instanciar el cliente de OpenAI
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai_api_key)


def obtener_respuesta(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ajusta el modelo según lo que necesites
        messages=[
            {"role": "system", "content": """
            Eres un financiero que trabaja para la consultora ABC experto en el área de solvencia,
            entonces vas a responder todo desde la perspectiva de la consultora. Contesta siempre en español
            en un máximo de 100 palabras.
            """},
            {"role": "user", "content": prompt}
        ]
    )
    output = response.choices[0].message.content
    return output

# Solicitar el prompt al usuario
prompt = st.text_area("Escribe tus dudas:")

if st.button("Obtener respuesta"):
    if prompt:
        output = obtener_respuesta(prompt)
        st.write("Respuesta:", output)
    else:
        st.write("Parece que no has hecho ninguna pregunta, intenta de nuevo.")

