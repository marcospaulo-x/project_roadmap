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
    st.markdown("""
        <style>
            .sidebar-content {
                display: flex;
                align-items: center;
                justify-content: flex-start;
                gap: 10px;
            }
            .home-button {
                cursor: pointer;
                background: none;
                border: none;
                padding: 5px;
            }
        </style>
        <div class="sidebar-content">
            <button class="home-button" onclick="window.location.reload();">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0078D7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 12l9-9 9 9"></path>
                    <path d="M9 21V9h6v12"></path>
                </svg>
            </button>
            <h1>📂 Seleção de Projetos e HUs</h1>
        </div>
    """, unsafe_allow_html=True)

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

    # Criar um container com altura flexível para empurrar os cards para o rodapé
    with st.container():
        st.markdown("<div style='height: 50vh;'></div>", unsafe_allow_html=True)  # Espaço para empurrar os cards

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div style="text-align: center; font-size: 20px; font-weight: bold;">📁 Total de Projetos</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; font-size: 24px; color: #0078D7;">{len(df_projetos)}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="text-align: center; font-size: 20px; font-weight: bold;">✅ Projetos Concluídos</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; font-size: 24px; color: #4CAF50;">{len(df_projetos[df_projetos["Status"] == "Concluído"])}</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div style="text-align: center; font-size: 20px; font-weight: bold;">🚀 Em Andamento</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; font-size: 24px; color: #FF9800;">{len(df_projetos[df_projetos["Status"] == "Em Andamento"])}</div>', unsafe_allow_html=True)

        st.markdown("---")

else:
    # Exibir detalhes da HU primeiro
    st.write(f"## 📋 Detalhes da HU {selected_hu_id}")
    hu_filtrada = df_hus[df_hus["ID"] == selected_hu_id]
    if not hu_filtrada.empty:
        hu_detalhes = hu_filtrada.iloc[0]
        
        def exibir_card(titulo, valor, icone, cor_borda="#0078D7", cor_texto="#fff"):
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {cor_borda};
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    color: {cor_texto};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    width: 100%;
                ">
                    <div style="font-size: 20px; font-weight: bold;">{icone} {titulo}</div>
                    <div style="font-size: 18px; font-weight: bold;">{valor}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        exibir_card("Descrição", hu_detalhes["Descrição"], "📝")
        exibir_card("Status", hu_detalhes["Status"], "📌")
        exibir_card("Progresso", f"{hu_detalhes['Progresso']}%", "📊")
        exibir_card("Data de Início", hu_detalhes["Data de Início"], "📅")
        exibir_card("Previsão de Conclusão", hu_detalhes["Previsão de Conclusão"], "⏳")

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
