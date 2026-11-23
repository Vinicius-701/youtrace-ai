# YouTrace AI: Observabilidade Preditiva e Triagem Autônoma


O **YouTrace AI** é uma ferramenta interna de inteligência operacional projetada para atuar nos bastidores da **YouShop**, conectando as áreas de **Atendimento**, **Qualidade (QA)** e **Desenvolvimento**. O sistema detecta falhas silenciosas em fluxos críticos de venda e comissionamento antes que gerem picos de chamados, traduz relatos vagos do suporte em roteiros reproduzíveis para QA e mantém a documentação técnica sincronizada com as alterações em produção.

## 1. Contextualização e Problema

A **YouShop** opera um ecossistema de vendas online onde marcas e produtores cadastram produtos físicos e digitais, creators geram links exclusivos rastreáveis para divulgação e a plataforma realiza a divisão automática de comissões a cada venda aprovada.

Durante períodos de lançamento ou ciclos acelerados de deploy, sistemas orientados a eventos estão sujeitos a **falhas silenciosas**. Nesses casos, a aplicação continua retornando sucesso (`HTTP 200`), sem disparar alertas tradicionais de indisponibilidade, mas quebra regras de negócio essenciais, como apagar o identificador de rastreamento de um creator quando o link contém parâmetros UTM externos.

### Gargalos Operacionais Mapeados

1. **Atendimento (Creator e Comprador):** Recebe reclamações urgentes e imprecisas (por exemplo, "meu link não marcou comissão" ou "o checkout deu erro"), sem visibilidade técnica do que ocorreu no sistema.
2. **Qualidade (QA):** Gasta horas tentando reproduzir defeitos descritos de forma vaga enquanto precisa acompanhar o ritmo rápido de entregas.
3. **Desenvolvimento:** Investiga incidentes em produção sob forte pressão de tempo, frequentemente apoiado em uma documentação técnica que ficou desatualizada após deploys recentes.

## 2. Como a Solução Funciona

Em vez de criar apenas um chatbot de atendimento (que trata o sintoma sem corrigir o defeito na origem) ou enviar milhões de logs brutos diretamente para uma LLM (o que seria caro e propenso a alucinações), o **YouTrace AI** combina **Machine Learning Clássico**, **RAG (Retrieval-Augmented Generation)** e **IA Generativa Estruturada** em quatro etapas sequenciais.

### Fluxo de Processamento

    [Logs de Produção + Chamado Vago do Suporte]
                           |
                           v
    1. Camada LGPD (modulos/privacidade.py)
       Mascara e-mails, CPFs e tokens sensíveis antes de qualquer análise.
                           |
                           v
    2. Sentinela Preditivo (modulos/detector_logs.py)
       Word2Vec + LocalOutlierFactor isolam anomalias silenciosas nos logs.
                           |
                           v
    3. Base Vetorial RAG (modulos/busca_rag.py)
       ChromaDB recupera regras de negócio e commits recentes relacionados ao caso.
                           |
                           v
    4. Agente de Triagem (modulos/agente_ia.py)
       Gemini 2.5 Flash (com Structured Output) + Fallback Local entregam:
         - Causa raiz e commit suspeito (para Desenvolvimento)
         - Passo a passo de reprodução (para QA)
         - Sugestão em formato Diff para atualizar a documentação (para Docs)

## 3. Estrutura do Projeto e Explicação dos Módulos

O projeto foi organizado de forma modular em Python para separar responsabilidades de interface, simulação de dados, governança de privacidade e modelos de inteligência artificial.

### Organização de Diretórios

    youtrace-ai/
    ├── .streamlit/
    │   └── config.toml            # Configuração visual do tema claro e identidade da marca
    ├── modulos/
    │   ├── __init__.py            # Inicializador do pacote Python
    │   ├── dados_simulados.py     # Simulação realista do ambiente da YouShop
    │   ├── privacidade.py         # Filtro de anonimização de dados sensíveis (LGPD)
    │   ├── detector_logs.py       # Pipeline de ML não supervisionado para logs
    │   ├── busca_rag.py           # Motor de busca semântica com ChromaDB em memória
    │   └── agente_ia.py           # Orquestrador de diagnóstico com Gemini e Pydantic
    ├── app.py                     # Interface web interativa (Streamlit)
    ├── requirements.txt           # Dependências do projeto
    ├── .env.example               # Modelo de configuração da chave de API
    └── .gitignore                 # Proteção contra versionamento de chaves e cache

### Resumo das Camadas

| Arquivo | Camada | Responsabilidade Principal |
| :--- | :--- | :--- |
| `app.py` | Apresentação | Interface web em Streamlit com indicadores, abas e cartões de diagnóstico. |
| `modulos/dados_simulados.py` | Dados | Base fictícia com docs desatualizadas, commits recentes, logs e chamados. |
| `modulos/privacidade.py` | Governança | Mascaramento automático de PII (e-mail, CPF e tokens) via Regex. |
| `modulos/detector_logs.py` | Machine Learning | Vetorização de logs (`Word2Vec`) e detecção de outliers (`LocalOutlierFactor`). |
| `modulos/busca_rag.py` | Busca Semântica | Indexação e consulta vetorial em memória utilizando `ChromaDB` e `TF-IDF`. |
| `modulos/agente_ia.py` | IA Generativa | Síntese estruturada (`Gemini 2.5 Flash` + `Pydantic`) com fallback local. |
| `.streamlit/config.toml` | Estilo | Padronização do tema claro e cores institucionais da YouShop. |

### Detalhamento Técnico de Cada Componente

#### `app.py` (Camada de Apresentação)
É o ponto de entrada da aplicação web construída com **Streamlit**. Exibe os indicadores consolidados no topo e divide a navegação em três abas: **Triagem de Incidentes** (onde o usuário testa chamados vagos e recebe o diagnóstico completo), **Monitoramento de Logs** (tabela com os scores de anomalia calculados pelo ML) e **Base de Conhecimento** (inspeção dos documentos e commits indexados).

#### `modulos/dados_simulados.py` (Ambiente Simulado)
Contém os dados que representam a operação da YouShop: documentos técnicos (incluindo uma documentação propositalmente desatualizada), histórico de commits recentes em produção, logs normais de checkout e comissão, logs com falhas silenciosas (`creator_id=NULL`) e exemplos de chamados reais do suporte.

#### `modulos/privacidade.py` (Governança LGPD)
Atua como barreira de segurança na entrada dos dados. Utiliza expressões regulares (*Regex*) para identificar e substituir e-mails, CPFs e tokens de sessão por marcadores neutros (`[EMAIL_OCULTO]`, `[CPF_OCULTO]` e `[TOKEN_OCULTO]`) antes da vetorização ou envio para modelos externos.

#### `modulos/detector_logs.py` (Sentinela Preditivo de Logs)
Implementa detecção de anomalias sem depender de regras manuais fixas. Primeiro, treina embeddings locais com **Word2Vec** (`gensim`) para capturar o contexto semântico das palavras de cada linha de log; em seguida, aplica o algoritmo **LocalOutlierFactor** (`scikit-learn`) para calcular um índice de anomalia e isolar eventos fora do padrão normal da operação.

#### `modulos/busca_rag.py` (Motor de Busca Semântica)
Utiliza o **ChromaDB** em modo efêmero (em memória RAM) combinado com vetorização **TF-IDF** (`scikit-learn`) para indexar tanto as regras oficiais do sistema quanto os *changelogs* de deploys recentes. Quando um chamado chega, recupera os trechos técnicos mais relevantes para ancorar a resposta da IA.

#### `modulos/agente_ia.py` (Agente de Diagnóstico e Documentação Viva)
Cruza o relato do atendimento, os documentos recuperados pelo ChromaDB e os logs anômalos isolados pelo ML. Utiliza a SDK oficial `google-genai` (`gemini-2.5-flash`) com **Structured Outputs** validados por **Pydantic** (`RelatorioDiagnostico`), garantindo que a saída siga sempre um contrato rígido. Caso a chave de API não esteja configurada, aciona automaticamente um motor determinístico local ancorado no RAG para garantir alta disponibilidade da demonstração.

#### `.streamlit/config.toml` (Identidade Visual)
Padroniza o tema claro (`light`) e aplica as cores institucionais da YouShop (azul-marinho `#0B2545` e verde-lima `#8CE000`), proporcionando uma experiência limpa de ferramenta interna de engenharia.

## 4. Como Executar Localmente

### Pré-requisitos

* Python **3.10** ou superior instalado.
* Chave de API do Google Gemini (opcional, pois o sistema possui fallback local integrado caso não seja informada).

### Passo a Passo de Instalação

1. Clone o repositório e acesse a pasta do projeto:

        git clone https://github.com/Vinicius-701/youtrace-ai.git
        cd youtrace-ai

2. Crie e ative um ambiente virtual isolado:

   No **Windows (PowerShell)**:

        python -m venv .venv
        .venv\Scripts\activate

   No **Linux ou macOS**:

        python3 -m venv .venv
        source .venv/bin/activate

3. Instale as dependências:

        pip install -r requirements.txt

4. Configure sua chave da API Gemini (opcional), criando um arquivo `.env` na raiz do projeto com base no `.env.example`:

        GEMINI_API_KEY=sua_chave_api_aqui

   *(Também é possível inserir a chave diretamente na barra lateral recolhível da interface web).*

5. Inicie a aplicação:

        streamlit run app.py

O painel abrirá automaticamente no navegador em `http://localhost:8501`.

## 5. Deploy em Nuvem (Streamlit Community Cloud)

Para disponibilizar o link público de acesso do protótipo:

1. Envie os arquivos para um repositório público no GitHub, garantindo que `.env` e `.venv/` estejam listados no `.gitignore`.
2. Acesse [share.streamlit.io](https://share.streamlit.io), conecte sua conta do GitHub e selecione o repositório e o arquivo principal `app.py`.
3. Caso queira habilitar a geração via Gemini diretamente no link público, acesse **Settings > Secrets** no painel do Streamlit Cloud e adicione:

        GEMINI_API_KEY = "sua_chave_aqui"

## 6. Limites Técnicos e Cuidados Éticos

### Controle Humano (Human-in-the-Loop)
O agente atua como copiloto de diagnóstico e sugestão. Ele nunca altera código em produção nem sobrescreve documentações oficiais automaticamente: toda atualização sugerida em `diff` exige revisão e aprovação de um desenvolvedor ou analista de QA.

### Privacidade by Design (LGPD)
Nenhum dado pessoal identificável (PII) ou token de autenticação trafega sem mascaramento prévio na camada de ingestão.

### Ancoragem contra Alucinações
O prompt do agente restringe o diagnóstico estritamente às evidências recuperadas nos logs e nos commits indexados via RAG, exibindo explicitamente as fontes consultadas na interface.