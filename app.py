import streamlit as st

from modulos.dados_simulados import (
    CHAMADOS_EXEMPLO,
    DOCUMENTOS_TECNICOS,
    LOGS_PRODUCAO,
)
from modulos.detector_logs import analisar_anomalias_logs
from modulos.busca_rag import BaseConhecimentoRAG
from modulos.agente_ia import gerar_diagnostico

st.set_page_config(
    page_title="YouTrace | Observabilidade e Triagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilo minimalista inspirado na identidade visual da YouShop
st.markdown(
    """
    <style>
        #MainMenu, footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        /* Cartões de métricas */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 1rem 1.25rem;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.82rem;
            color: #64748B;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.65rem;
            color: #0B2545;
            font-weight: 700;
        }
        /* Botão principal */
        div.stButton > button[kind="primary"] {
            background-color: #0B2545;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #163A6B;
            color: #FFFFFF;
        }
        /* Cabeçalho customizado */
        .top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.25rem;
        }
        .brand-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0B2545;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .brand-badge {
            background-color: #ECFCCB;
            color: #365314;
            border: 1px solid #BEF264;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            margin-left: 0.6rem;
            vertical-align: middle;
        }
        .brand-subtitle {
            color: #475569;
            font-size: 0.98rem;
            margin-bottom: 1.5rem;
        }
        .section-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }
        .meta-pill {
            display: inline-block;
            background-color: #F1F5F9;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 500;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            margin-right: 0.5rem;
            margin-bottom: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def iniciar_rag() -> BaseConhecimentoRAG:
    return BaseConhecimentoRAG(DOCUMENTOS_TECNICOS)


@st.cache_data
def carregar_logs():
    return analisar_anomalias_logs(LOGS_PRODUCAO)


rag = iniciar_rag()
tabela_logs = carregar_logs()

# Barra lateral recolhida por padrão (apenas configuração)
with st.sidebar:
    st.markdown("### Configurações")
    chave_gemini = st.text_input(
        "Chave da API Gemini (opcional)",
        type="password",
        placeholder="AIza...",
        help="Quando preenchida, utiliza o modelo Gemini 2.5 Flash. Caso contrário, opera com o motor local.",
    )
    st.caption("Logs anonimizados automaticamente conforme diretrizes LGPD antes de qualquer processamento.")

# Cabeçalho limpo
st.markdown(
    """
    <div class="top-bar">
        <div>
            <span class="brand-title">YouTrace</span>
            <span class="brand-badge">Engenharia &amp; Operações</span>
        </div>
    </div>
    <p class="brand-subtitle">
        Correlação entre relatos de atendimento, anomalias em logs de produção e base técnica.
    </p>
    """,
    unsafe_allow_html=True,
)

# Indicadores superiores
col1, col2, col3, col4 = st.columns(4)
total_anomalias = int(tabela_logs["eh_anomalia"].sum())
col1.metric("Eventos monitorados", f"{len(tabela_logs)}")
col2.metric("Anomalias isoladas", f"{total_anomalias}", delta="Detectadas pré-chamado", delta_color="off")
col3.metric("Documentos indexados", f"{rag.total_documentos()}")
col4.metric("Tempo médio de triagem", "18 s", delta="Antes: ~2h 30m", delta_color="off")

st.write("")

aba_triagem, aba_logs, aba_base = st.tabs([
    "Triagem de Incidentes",
    "Monitoramento de Logs",
    "Base de Conhecimento",
])

with aba_triagem:
    with st.container(border=True):
        st.markdown('<div class="section-label">Entrada do Atendimento</div>', unsafe_allow_html=True)
        opcao = st.selectbox(
            "Cenário de chamado",
            list(CHAMADOS_EXEMPLO.keys()),
            label_visibility="collapsed",
        )
        texto_chamado = st.text_area(
            "Descrição do relato",
            value=CHAMADOS_EXEMPLO[opcao],
            height=85,
            placeholder="Descreva o problema relatado pelo creator ou comprador...",
            label_visibility="collapsed",
        )
        executar = st.button("Analisar incidente", type="primary")

    if executar:
        if not texto_chamado.strip():
            st.warning("Insira a descrição do relato antes de iniciar a análise.")
        else:
            with st.spinner("Consultando base técnica e cruzando eventos anômalos..."):
                trechos = rag.buscar_contexto(texto_chamado)
                logs_com_erro = tabela_logs[tabela_logs["eh_anomalia"]]["log_seguro"].tolist()
                relatorio, motor = gerar_diagnostico(texto_chamado, trechos, logs_com_erro, chave_gemini)

            st.write("")
            st.markdown(
                f'<span class="meta-pill">Motor: {motor}</span>'
                f'<span class="meta-pill">Confiança: {relatorio.nivel_confianca}</span>'
                f'<span class="meta-pill">Evidências cruzadas: {len(trechos)} docs · {len(logs_com_erro)} logs</span>',
                unsafe_allow_html=True,
            )

            col_dev, col_qa = st.columns(2, gap="medium")

            with col_dev:
                with st.container(border=True):
                    st.markdown('<div class="section-label">Diagnóstico · Desenvolvimento</div>', unsafe_allow_html=True)
                    st.markdown(f"**Serviço afetado:** `{relatorio.servico_afetado}`")
                    st.markdown(f"**Alteração suspeita:** `{relatorio.commit_suspeito}`")
                    st.divider()
                    st.markdown("**Causa raiz provável**")
                    st.write(relatorio.causa_raiz)

            with col_qa:
                with st.container(border=True):
                    st.markdown('<div class="section-label">Reprodução · Qualidade (QA)</div>', unsafe_allow_html=True)
                    st.markdown(f"**Pré-condições:** {relatorio.pre_condicoes_qa}")
                    st.divider()
                    st.markdown("**Passos para reprodução**")
                    for idx, passo in enumerate(relatorio.passos_reproducao, start=1):
                        st.markdown(f"{idx}. {passo}")
                    st.markdown(f"**Comportamento atual:** {relatorio.resultado_obtido}")
                    st.markdown(f"**Comportamento esperado:** {relatorio.resultado_esperado}")

            with st.container(border=True):
                st.markdown('<div class="section-label">Atualização sugerida · Documentação técnica</div>', unsafe_allow_html=True)
                st.code(relatorio.sugestao_documentacao, language="diff")

            with st.expander("Fontes consultadas na base vetorial (ChromaDB)"):
                for t in trechos:
                    st.markdown(f"**{t['titulo']}** — *{t['tipo']}*")
                    st.caption(t["conteudo"])

with aba_logs:
    with st.container(border=True):
        topo_logs_1, topo_logs_2 = st.columns([3, 1])
        with topo_logs_1:
            st.markdown('<div class="section-label">Eventos em produção (Word2Vec + LocalOutlierFactor)</div>', unsafe_allow_html=True)
        with topo_logs_2:
            filtrar = st.checkbox("Apenas anomalias", value=False)

        dados_exibir = tabela_logs[tabela_logs["eh_anomalia"]].copy() if filtrar else tabela_logs.copy()
        dados_exibir["status_limpo"] = dados_exibir["eh_anomalia"].map(
            {True: "Anomalia", False: "Normal"}
        )

        st.dataframe(
            dados_exibir[["status_limpo", "pontuacao_anomalia", "log_seguro"]].rename(
                columns={
                    "status_limpo": "Classificação",
                    "pontuacao_anomalia": "Score",
                    "log_seguro": "Evento (Anonimizado LGPD)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with aba_base:
    st.markdown('<div class="section-label">Documentos e commits indexados em memória</div>', unsafe_allow_html=True)
    for doc in DOCUMENTOS_TECNICOS:
        with st.container(border=True):
            st.markdown(f"**{doc['titulo']}**")
            st.caption(doc["tipo"])
            st.write(doc["conteudo"])