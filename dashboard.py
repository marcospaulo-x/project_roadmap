import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Configuração para acessar o Google Sheets usando Streamlit Secrets
SHEET_ID = "1QmdhLGP516CoHxDbORqw2ZV-F2_4UzKjxMfOrJnOFEA"

# Carregar credenciais do Streamlit Secrets
credentials_dict = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
gc = gspread.authorize(credentials)

# Carregar dados do Google Sheets
sh = gc.open_by_key(SHEET_ID)
df_projetos = pd.DataFrame(sh.worksheet("Projetos").get_all_records())
df_hus = pd.DataFrame(sh.worksheet("HUs").get_all_records())

# Título do Dashboard
st.title("📊 Roadmap de Projetos e HUs")

# Separador visual
st.markdown("---")

# Métricas principais
col1, col2, col3 = st.columns(3)
col1.metric("📁 Total de Projetos", len(df_projetos))
col2.metric("✅ Projetos Concluídos", len(df_projetos[df_projetos["Status"] == "Concluído"]))
col3.metric("🚀 Em Andamento", len(df_projetos[df_projetos["Status"] == "Em Andamento"]))

st.markdown("---")

# Visão Geral dos Projetos
st.write("## 🚀 Visão Geral dos Projetos")
fig = px.bar(df_projetos, x="Nome do projeto", y="Progresso", color="Status", title="Progresso dos Projetos")
st.plotly_chart(fig)

# Detalhes dos Projetos
st.write("## 📋 Detalhes dos Projetos")
projeto_selecionado = st.selectbox("Selecione um projeto", df_projetos["Nome do projeto"])

# Filtrar HUs do projeto selecionado corretamente
hus_projeto = df_hus[df_hus["Projeto"] == projeto_selecionado]

# Exibir HUs do Projeto
st.write(f"### Histórias de Usuário - {projeto_selecionado}")

# Gráfico de Barras Interativo
fig_hus = px.bar(
    hus_projeto,
    x="Descrição",
    y="Progresso",
    color="Status",
    title=f"Progresso das HUs - {projeto_selecionado}",
    hover_data=["Data de Início", "Previsão de Conclusão", "Status"],
    labels={"Descrição": "HU", "Progresso": "Progresso (%)"},
)

fig_hus.update_traces(
    hovertemplate="<b>%{x}</b><br>Progresso: %{y}%<br>Início: %{customdata[0]}<br>Previsão: %{customdata[1]}<br>Status: %{customdata[2]}"
)

st.plotly_chart(fig_hus, use_container_width=True)

# Exibir detalhes da HU selecionada
st.write("### Detalhes da HU Selecionada")
selected_hu_id = st.selectbox("Selecione uma HU...", hus_projeto["Descrição"])
hu_detalhada = hus_projeto[hus_projeto["Descrição"] == selected_hu_id]
st.write(hu_detalhada)
