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

# Configuração do Sidebar
with st.sidebar:
    st.title("📂 Seleção de Projetos e HUs")
    projeto_selecionado = st.selectbox("Selecione um projeto", ["Selecionar"] + list(df_projetos["Nome do projeto"]))
    
    if projeto_selecionado != "Selecionar":
        hus_projeto = df_hus[df_hus["Projeto"] == projeto_selecionado]
        if not hus_projeto.empty:
            selected_hu_id = st.selectbox("Selecione uma HU", hus_projeto["ID"].tolist())
        else:
            selected_hu_id = None
    else:
        selected_hu_id = None

# Tela inicial limpa
if projeto_selecionado == "Selecionar":
    st.title("📊 Roadmap de Projetos e HUs")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📁 Total de Projetos", len(df_projetos))
    col2.metric("✅ Projetos Concluídos", len(df_projetos[df_projetos["Status"] == "Concluído"]))
    col3.metric("🚀 Em Andamento", len(df_projetos[df_projetos["Status"] == "Em Andamento"]))
    
    st.markdown("---")
    st.markdown("## 🔹 Squad Conta")
else:
    # Exibir detalhes da HU primeiro
    st.write(f"## 📋 Detalhes da HU {selected_hu_id}")
    hu_filtrada = df_hus[df_hus["ID"] == selected_hu_id]
    if not hu_filtrada.empty:
        hu_detalhes = hu_filtrada.iloc[0]
        
        def exibir_card(titulo, valor, icone, cor_fundo="white", cor_texto="black"):
            st.markdown(
                f"""
                <div style="
                    background-color: {cor_fundo};
                    padding: 10px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    margin: 5px 0;
                    color: {cor_texto};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div style="font-size: 24px; font-weight: bold;">{icone} {titulo}</div>
                    <div style="font-size: 20px; font-weight: bold;">{valor}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        exibir_card("Descrição", hu_detalhes["Descrição"], "📝", "#f0f8ff", "#333")
        exibir_card("Status", hu_detalhes["Status"], "📌", "#fff3cd", "#856404")
        exibir_card("Progresso", f"{hu_detalhes['Progresso']}%", "📊", "#e2f0d9", "#4caf50")
        exibir_card("Data de Início", hu_detalhes["Data de Início"], "📅", "#e3f2fd", "#0d47a1")
        exibir_card("Previsão de Conclusão", hu_detalhes["Previsão de Conclusão"], "⏳", "#ffebee", "#c62828")

        st.write("### Progresso da HU")
        st.progress(hu_detalhes["Progresso"] / 100)
        
        st.markdown("---")
    else:
        st.warning("Nenhuma HU encontrada para o projeto selecionado.")
    
    # Visão Geral dos Projetos abaixo dos detalhes da HU
    st.write("## 🚀 Visão Geral dos Projetos")
    fig = px.bar(df_projetos, x="Nome do projeto", y="Progresso", color="Status", title="Progresso dos Projetos", 
                 color_discrete_map={"Em Andamento": "#FFCC00", "Concluído": "#4CAF50"})
    st.plotly_chart(fig)
