import streamlit as st
import pandas as pd
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
gc = gspread.authorize(credentials)

# Carregar dados do Google Sheets
sh = gc.open_by_key(SHEET_ID)
df_projetos = pd.DataFrame(sh.worksheet("Projetos").get_all_records())

# Total de projetos, concluídos e em andamento
total_projetos = len(df_projetos)
concluidos = len(df_projetos[df_projetos["Status"] == "Concluído"])
andamento = len(df_projetos[df_projetos["Status"] == "Em Andamento"])

# Estilo personalizado
st.markdown(
    """
    <style>
        .info-card {
            display: flex;
            justify-content: space-around;
            align-items: center;
            border: 2px solid #0078D7;
            padding: 15px;
            border-radius: 12px;
            max-width: 700px;
            margin: 30px auto;
        }
        .info-card div {
            text-align: center;
            flex: 1;
        }
        .info-card h3 {
            margin: 0;
            color: #0078D7;
            font-size: 18px;
        }
        .info-card p {
            margin: 5px 0;
            font-size: 22px;
            font-weight: bold;
        }
        .home-button {
            position: absolute;
            top: 15px;
            left: 15px;
            cursor: pointer;
        }
        .home-button svg {
            color: #0078D7;
            width: 30px;
            height: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Botão Home com SVG
st.markdown(
    """
    <div class="home-button" onclick="window.location.href='/'">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9L12 2L21 9"></path>
            <path d="M9 22V12H15V22"></path>
        </svg>
    </div>
    """,
    unsafe_allow_html=True
)

# Exibir o card de informações
st.markdown(
    f"""
    <div class="info-card">
        <div>
            <h3>📁 Total de Projetos</h3>
            <p>{total_projetos}</p>
        </div>
        <div>
            <h3>✅ Concluídos</h3>
            <p style="color: #4CAF50;">{concluidos}</p>
        </div>
        <div>
            <h3>🚀 Em Andamento</h3>
            <p style="color: #FF9800;">{andamento}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
