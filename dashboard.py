import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração para acessar o Google Sheets usando Streamlit Secrets
SHEET_ID = "1QmdhLGP516CoHxDbORqw2ZV-F2_4UzKjxMfOrJnOFEA"

# Carregar credenciais do Streamlit Secrets
credentials_dict = st.secrets["gcp_service_account"]

# Usar as credenciais do Google diretamente
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict, 
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
# Autorizar com o Google
gc = gspread.authorize(credentials)

# Carregar dados do Google Sheets
sh = gc.open_by_key(SHEET_ID)
df_projetos = pd.DataFrame(sh.worksheet("Projetos").get_all_records())
df_hus = pd.DataFrame(sh.worksheet("HUs").get_all_records())

# Sidebar para seleção de projeto e HU
st.sidebar.title("📁 Projetos e Histórias de Usuário")
projeto_selecionado = st.sidebar.selectbox("Selecione um projeto", df_projetos["Nome do projeto"].unique())

# Filtrar HUs do projeto selecionado
hus_projeto = df_hus[df_hus["Projeto"] == projeto_selecionado]

if not hus_projeto.empty:
    hu_selecionada = st.sidebar.selectbox("Selecione uma HU", hus_projeto["ID"] + " - " + hus_projeto["Descrição"])
    
    # Pegar ID real da HU selecionada
    selected_hu_id = hu_selecionada.split(" - ")[0]
    hu_detalhes = hus_projeto[hus_projeto["ID"] == selected_hu_id].iloc[0]
else:
    st.sidebar.warning("Nenhuma HU disponível para este projeto.")
    hu_detalhes = None

# Título do Dashboard
st.title("📊 Roadmap de Projetos e HUs")
st.markdown("---")

# 📌 Melhorando a exibição das métricas
col1, col2, col3 = st.columns(3)
col1.metric("📁 Total de Projetos", len(df_projetos))
col2.metric("✅ Projetos Concluídos", len(df_projetos[df_projetos["Status"] == "Concluído"]))
col3.metric("🚀 Em Andamento", len(df_projetos[df_projetos["Status"] == "Em Andamento"]))
st.markdown("---")

# Visão Geral dos Projetos
st.write("## 🚀 Visão Geral dos Projetos")
fig = px.bar(df_projetos, x="Nome do projeto", y="Progresso", color="Status", title="Progresso dos Projetos", 
             color_discrete_map={"Em Andamento": "#FFCC00", "Concluído": "#4CAF50"})
st.plotly_chart(fig)

# Exibir detalhes da HU selecionada, se houver
if hu_detalhes is not None:
    st.write(f"## 📋 Detalhes da HU {hu_detalhes['ID']}")
    st.write(f"**Descrição:** {hu_detalhes['Descrição']}")
    st.write(f"**Status:** {hu_detalhes['Status']}")
    st.write(f"**Progresso:** {hu_detalhes['Progresso']}%")
    st.write(f"**Data de Início:** {hu_detalhes['Data de Início']}")
    st.write(f"**Previsão de Conclusão:** {hu_detalhes['Previsão de Conclusão']}")
    
    # Adicionar barra de progresso
    st.progress(hu_detalhes["Progresso"] / 100)
    st.markdown("---")
