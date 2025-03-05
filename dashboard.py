import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Roadmap de Projetos", layout="centered", initial_sidebar_state="collapsed")

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
    st.markdown(
        """
        <style>
        .sidebar-button {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            margin-left: 12px;
        }
        .sidebar-button svg {
            cursor: pointer;
            color: #0078D7;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Botão de Home no Sidebar (alinhado corretamente)
    if st.button("", key="home_button"):
        st.experimental_rerun()
    
    st.markdown(
        """
        <div class="sidebar-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9L12 2L21 9"></path>
                <path d="M9 22V12H15V22"></path>
            </svg>
        </div>
        """,
        unsafe_allow_html=True
    )

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
    st.markdown(
        """
        <h1 style="text-align: center; color: #fff;">📊 Roadmap de Projetos e HU's</h1>
        <h2 style="text-align: center; color: #0078D7;">Squad Conta</h2>
        <p style="text-align: center; font-size: 17px; color: #fff;">
            Bem-vindo ao painel de projetos!<br>Selecione um projeto e uma HU no menu lateral para visualizar os detalhes.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Card com informações lado a lado
    total_projetos = len(df_projetos)
    concluidos = len(df_projetos[df_projetos["Status"] == "Concluído"])
    andamento = len(df_projetos[df_projetos["Status"] == "Em Andamento"])

    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            border: 2px solid #0078D7;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 50px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        ">
            <div style="flex: 1;">
                <h3 style="color: #0078D7;">📁 Total de Projetos</h3>
                <p style="font-size: 24px; font-weight: bold; color: #0078D7;">{total_projetos}</p>
            </div>
            <div style="flex: 1;">
                <h3 style="color: #4CAF50;">✅ Concluídos</h3>
                <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{concluidos}</p>
            </div>
            <div style="flex: 1;">
                <h3 style="color: #FF9800;">🚀 Em Andamento</h3>
                <p style="font-size: 24px; font-weight: bold; color: #FF9800;">{andamento}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

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

