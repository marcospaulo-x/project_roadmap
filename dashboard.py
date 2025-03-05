import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Configuração da página
st.set_page_config(
    page_title="Roadmap de Projetos",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)

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

# Sidebar para seleção de projetos e HUs
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

# Estilos CSS personalizados
st.markdown(
    """
    <style>
        .card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            text-align: center;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .card h3 {
            font-size: 20px;
            color: #333;
        }
        .card p {
            font-size: 24px;
            color: #0078D7;
            font-weight: bold;
        }
        .welcome-text {
            text-align: center;
            font-size: 18px;
            color: #fff;
            margin-bottom: 30px;
        }
        .section-title {
            text-align: center;
            font-size: 24px;
            color: #0078D7;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Tela inicial
if projeto_selecionado == "Selecionar":
    # Título e animação
    st.markdown('<h1 style="text-align: center; color: #fff;">📊 Roadmap de Projetos e HU\'s</h1>', unsafe_allow_html=True)
    
    # Mensagem de boas-vindas
    st.markdown(
        """
        <div class="welcome-text">
            Olá, seja bem-vindo(a)!<br>Explore os projetos e acompanhe o progresso das HUs.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cards de métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="card"><h3>📁 Total de Projetos</h3><p>{}</p></div>'.format(len(df_projetos)),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="card"><h3>✅ Projetos Concluídos</h3><p>{}</p></div>'.format(len(df_projetos[df_projetos["Status"] == "Concluído"])),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="card"><h3>🚀 Em Andamento</h3><p>{}</p></div>'.format(len(df_projetos[df_projetos["Status"] == "Em Andamento"])),
            unsafe_allow_html=True,
        )

    # Gráfico de distribuição de status
    st.markdown('<div class="section-title">Distribuição de Status dos Projetos</div>', unsafe_allow_html=True)
    status_counts = df_projetos["Status"].value_counts()
    fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title="")
    st.plotly_chart(fig, use_container_width=True)

    # Botão para atualizar dados
    if st.button("🔄 Atualizar Dados"):
        st.experimental_rerun()

# Tela de detalhes do projeto e HU
else:
    # Detalhes da HU
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
    
    # Visão Geral dos Projetos
    st.write("## 🚀 Visão Geral dos Projetos")
    fig = px.bar(df_projetos, x="Nome do projeto", y="Progresso", color="Status", title="Progresso dos Projetos", 
                 color_discrete_map={"Em Andamento": "#FFCC00", "Concluído": "#4CAF50"})
    st.plotly_chart(fig, use_container_width=True)