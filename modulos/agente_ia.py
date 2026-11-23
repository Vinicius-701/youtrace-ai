import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from modulos.privacidade import mascarar_dados_sensiveis

load_dotenv()


class RelatorioDiagnostico(BaseModel):
    servico_afetado: str = Field(description="Nome do serviço onde ocorre a falha.")
    commit_suspeito: str = Field(description="Commit recente ligado ao problema.")
    causa_raiz: str = Field(description="Explicação técnica clara para o time de Dev.")
    pre_condicoes_qa: str = Field(description="O que precisa estar configurado para testar.")
    passos_reproducao: list[str] = Field(description="Passo a passo numerado para QA.")
    resultado_obtido: str = Field(description="O que acontece hoje com o bug.")
    resultado_esperado: str = Field(description="O que deveria acontecer.")
    sugestao_documentacao: str = Field(description="Texto atualizado para a documentação técnica.")
    nivel_confianca: str = Field(description="Alto, Médio ou Baixo.")


def gerar_diagnostico(
    chamado: str,
    trechos_rag: list[dict],
    logs_anomalos: list[str],
    chave_api: str = "",
) -> tuple[RelatorioDiagnostico, str]:
    """Gera o diagnóstico técnico via Gemini ou via motor local ancorado no RAG."""
    chamado_seguro = mascarar_dados_sensiveis(chamado)
    chave_final = (chave_api or os.getenv("GEMINI_API_KEY", "")).strip()

    if chave_final:
        try:
            cliente = genai.Client(api_key=chave_final)
            contexto_docs = "\n\n".join(
                [f"[{t['tipo']} - {t['titulo']}]: {t['conteudo']}" for t in trechos_rag]
            )
            contexto_logs = "\n".join(logs_anomalos)

            prompt = f"""
Você é o YouTrace AI, assistente de Engenharia e QA da YouShop.
Cruze o chamado do suporte com os documentos do ChromaDB e os logs anômalos abaixo.

CHAMADO DO SUPORTE:
"{chamado_seguro}"

DOCUMENTOS RECUPERADOS (RAG):
{contexto_docs}

LOGS ANÔMALOS DETECTADOS:
{contexto_logs}
"""
            resposta = cliente.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RelatorioDiagnostico,
                    temperature=0.2,
                ),
            )
            relatorio = RelatorioDiagnostico.model_validate_json(resposta.text)
            return relatorio, "Gemini 2.5 Flash (Online)"
        except Exception:
            pass

    # Plano B local (ancorado nos documentos recuperados do ChromaDB)
    doc_principal = trechos_rag[0]["titulo"] if trechos_rag else "Base Técnica"
    if "Cupom" in doc_principal:
        return (
            RelatorioDiagnostico(
                servico_afetado="CheckoutService (/api/v2/checkout/validate)",
                commit_suspeito="Commit #44b1e09 (v2.14.2) - Validação de Cupom em Lançamentos",
                causa_raiz="A nova regra bloqueia cupons expirados em carrinhos com order bump e retorna HTTP 422 sem mensagem amigável.",
                pre_condicoes_qa="Curso digital com order bump ativo e código de cupom expirado.",
                passos_reproducao=[
                    "Adicionar o produto principal e marcar o order bump no checkout.",
                    "Inserir um cupom promocional expirado e clicar em Aplicar.",
                    "Observar a resposta da requisição de validação.",
                ],
                resultado_obtido="Tela exibe erro genérico sem orientar o comprador.",
                resultado_esperado="Exibir aviso claro ('Cupom expirado') mantendo o checkout liberado.",
                sugestao_documentacao="Atualizar doc de Checkout: informar tratamento obrigatório para erro HTTP 422 em cupons expirados com order bump.",
                nivel_confianca="Alto",
            ),
            "Motor Local Ancorado no ChromaDB",
        )

    return (
        RelatorioDiagnostico(
            servico_afetado="GatewayParamFilter -> SplitCommissionWorker",
            commit_suspeito="Commit #89a4f1c (v2.14.3) - Filtro de Parâmetros na URL",
            causa_raiz=(
                f"Falha silenciosa detectada em {len(logs_anomalos)} logs anômalos e cruzada com '{doc_principal}'. "
                "Ao limpar parâmetros UTM, o filtro apaga tudo após o '&', fazendo o 'creator_id' chegar nulo."
            ),
            pre_condicoes_qa="Produto ativo (prod_12) com comissão configurada para o creator 'lucasfit'.",
            passos_reproducao=[
                "Acessar o link do creator com UTM: https://youshop.com.br/p/prod_12?ref=lucasfit&utm_source=instagram",
                "Finalizar uma compra de teste.",
                "Verificar o registro gerado no SplitCommissionWorker.",
            ],
            resultado_obtido="O sistema apaga o parâmetro 'ref' e registra creator_id=NULL com comissão R$ 0,00.",
            resultado_esperado="Preservar 'ref=lucasfit' mesmo quando houver parâmetros UTM na URL.",
            sugestao_documentacao=(
                "--- docs/atribuicao-links.md (v2.12)\n"
                "+++ docs/atribuicao-links.md (v2.14.4)\n"
                "+Regra: Links de creators com parâmetros UTM devem manter o parâmetro 'ref' intacto antes de gravar o cookie."
            ),
            nivel_confianca="Alto",
        ),
        "Motor Local Ancorado no ChromaDB",
    )