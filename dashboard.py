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

# Título do Dashboard
st.title("📊 Roadmap de Projetos e HUs")

# Separador visual
st.markdown("---")

# 📌 Melhorando a exibição das métricas com emojis para facilitar a leitura
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

# Detalhes dos Projetos
st.write("## 📋 Detalhes dos Projetos")
projeto_selecionado = st.selectbox("Selecione um projeto", df_projetos["Nome do projeto"])

# Filtrar HUs do projeto selecionado corretamente
hus_projeto = df_hus[df_hus["Projeto"] == projeto_selecionado]

# Verificar se há HUs para o projeto selecionado
if hus_projeto.empty:
    # Exibir aviso
    st.warning("Ops, ainda não foi adicionado HU's neste projeto. Não se preocupe, em breve será adicionado! 😉")
else:
    # Exibir HUs do Projeto
    st.write(f"### Histórias de Usuário - {projeto_selecionado}")

    # Gráfico de Barras Interativo
    fig_hus = px.bar(
        hus_projeto,
        x="Descrição",  # Descrição da HU no eixo X
        y="Progresso",  # Progresso da HU no eixo Y
        color="Status",  # Cor das barras por status
        title=f"Progresso das HUs - {projeto_selecionado}",
        hover_data=["Data de Início", "Previsão de Conclusão", "Status"],  # Informações no tooltip
        labels={"Descrição": "HU", "Progresso": "Progresso (%)"},
    )

    # Adicionar interatividade ao gráfico
    fig_hus.update_traces(
        hovertemplate="<b>%{x}</b><br>Progresso: %{y}%<br>Início: %{customdata[0]}<br>Previsão: %{customdata[1]}<br>Status: %{customdata[2]}"
    )

    # Exibir o gráfico
    st.plotly_chart(fig_hus, use_container_width=True)

    # Exibir detalhes da HU selecionada
    st.write("### Detalhes da HU Selecionada")

    # Selecionar a HU pelo ID
    selected_hu_id = st.selectbox("Selecione uma HU para ver detalhes", hus_projeto["ID"])

    # Filtrar a HU selecionada
    hu_filtrada = hus_projeto[hus_projeto["ID"] == selected_hu_id]

    # Verificar se a HU filtrada não está vazia
    if not hu_filtrada.empty:
        hu_detalhes = hu_filtrada.iloc[0]

        # Função para exibir um card estilizado
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

        # Exibir cards estilizados
        exibir_card("Descrição", hu_detalhes["Descrição"], "📝", "#f0f8ff", "#333")
        exibir_card("Status", hu_detalhes["Status"], "📌", "#fff3cd", "#856404")
        exibir_card("Progresso", f"{hu_detalhes['Progresso']}%", "📊", "#e2f0d9", "#4caf50")
        exibir_card("Data de Início", hu_detalhes["Data de Início"], "📅", "#e3f2fd", "#0d47a1")
        exibir_card("Previsão de Conclusão", hu_detalhes["Previsão de Conclusão"], "⏳", "#ffebee", "#c62828")

        # Adicionar uma barra de progresso estilizada
        st.write("### Progresso da HU")
        st.progress(hu_detalhes["Progresso"] / 100)

        # Adicionar um separador
        st.markdown("---")
    else:
        st.warning("No momento não foi adicionado HU's para o projeto selecionado.")
