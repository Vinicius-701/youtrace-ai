DOCUMENTOS_TECNICOS = [
    {
        "id": "doc_atribuicao_01",
        "tipo": "Documentação Técnica (Desatualizada)",
        "titulo": "Regra de Atribuição de Links de Creators (v2.12)",
        "conteudo": (
            "REGRA OFICIAL DE RASTREAMENTO: Todo link exclusivo de creator segue o formato "
            "youshop.com.br/p/{produto_id}?ref={creator_id}. Ao clicar, o serviço AttributionService "
            "grava o cookie 'ys_ref' válido por 30 dias e envia o parâmetro 'creator_id' no checkout. "
            "A comissão é dividida automaticamente após o pagamento aprovado."
        ),
    },
    {
        "id": "commit_89a4f",
        "tipo": "Commit Recente em Produção",
        "titulo": "Commit #89a4f1c (Deploy há 2h) - Filtro de Parâmetros na URL",
        "conteudo": (
            "ALTERAÇÃO RECENTE (v2.14.3): Adicionado filtro no CheckoutService para remover parâmetros "
            "externos (utm_campaign, fbclid) e melhorar o cache. Bug colateral: quando o link do creator "
            "vem com UTMs anexados (ex: ?ref=lucasfit&utm_source=instagram), o filtro apaga tudo após o '&', "
            "fazendo o campo 'creator_id' chegar vazio (NULL) na divisão de comissões."
        ),
    },
    {
        "id": "doc_webhook_02",
        "tipo": "Documentação Técnica",
        "titulo": "Processamento de Webhooks de Pagamento",
        "conteudo": (
            "FLUXO DE PAGAMENTO: O gateway envia eventos PIX_PAID e CARD_APPROVED para a fila de "
            "pagamentos. Se o processamento demorar mais de 5 segundos, ocorre timeout HTTP 504 e "
            "o evento entra em nova tentativa automática."
        ),
    },
    {
        "id": "commit_44b1e",
        "tipo": "Commit Recente em Produção",
        "titulo": "Commit #44b1e09 (Deploy há 5h) - Validação de Cupom em Lançamentos",
        "conteudo": (
            "ALTERAÇÃO RECENTE (v2.14.2): Nova regra impede acumular dois cupons no mesmo carrinho. "
            "Se o comprador tentar usar um cupom expirado em produto com order bump ativo, a API "
            "retorna erro HTTP 422 sem exibir mensagem explicativa na tela."
        ),
    },
]

LOGS_PRODUCAO = [
    "2026-11-22 19:01:10 INFO CheckoutService: pedido=9011 produto=prod_44 creator_id=ana_beauty status=APROVADO",
    "2026-11-22 19:01:15 INFO AttributionService: clique_registrado ref=marcos_tech cookie=ys_ref_ok latencia=18ms",
    "2026-11-22 19:01:22 INFO SplitCommissionWorker: pedido=9011 creator_id=ana_beauty comissao=R$45.00 status=AGENDADO",
    "2026-11-22 19:01:30 INFO CheckoutService: pedido=9012 produto=prod_12 creator_id=carol_fit status=APROVADO",
    "2026-11-22 19:01:41 INFO AttributionService: clique_registrado ref=pedro_dev cookie=ys_ref_ok latencia=21ms",
    "2026-11-22 19:01:55 INFO SplitCommissionWorker: pedido=9012 creator_id=carol_fit comissao=R$89.90 status=AGENDADO",
    "2026-11-22 19:02:04 INFO CheckoutService: pedido=9013 produto=prod_44 creator_id=ana_beauty status=APROVADO",
    "2026-11-22 19:02:18 INFO WebhookConsumer: evento=PIX_PAID pedido=9013 tempo=140ms",
    "2026-11-22 19:02:29 INFO CheckoutService: pedido=9014 produto=prod_99 creator_id=bia_makeup status=APROVADO",
    "2026-11-22 19:02:40 INFO SplitCommissionWorker: pedido=9014 creator_id=bia_makeup comissao=R$32.50 status=AGENDADO",
    "2026-11-22 19:02:51 INFO WebhookConsumer: evento=CARD_APPROVED pedido=9014 tempo=165ms",
    "2026-11-22 19:03:02 INFO AttributionService: clique_registrado ref=julia_livros cookie=ys_ref_ok latencia=19ms",
    "2026-11-22 19:03:14 INFO CheckoutService: pedido=9015 produto=prod_12 creator_id=pedro_dev status=APROVADO",
    "2026-11-22 19:03:25 INFO SplitCommissionWorker: pedido=9015 creator_id=pedro_dev comissao=R$89.90 status=AGENDADO",
    # Falhas silenciosas após o deploy v2.14.3
    "2026-11-22 19:04:01 WARN GatewayParamFilter: url_cortada query=ref=lucasfit&utm_source=instagram token=segredo9988",
    "2026-11-22 19:04:03 WARN SplitCommissionWorker: pedido=9016 produto=prod_12 creator_id=NULL origem=organico comissao=R$0.00",
    "2026-11-22 19:04:19 WARN GatewayParamFilter: url_cortada query=ref=lucasfit&utm_campaign=lancamento email=lucas@email.com",
    "2026-11-22 19:04:21 WARN SplitCommissionWorker: pedido=9017 produto=prod_12 creator_id=NULL origem=organico comissao=R$0.00",
]

CHAMADOS_EXEMPLO = {
    "Cenário 1 (Creator - Comissão Zerada)": (
        "O creator @lucasfit abriu chamado urgente dizendo que divulgou o link do produto nos "
        "stories do Instagram ontem, vários seguidores compraram, mas no painel dele consta R$ 0,00 de comissão."
    ),
    "Cenário 2 (Comprador - Erro no Cupom)": (
        "Cliente reclamando que tentou aplicar um cupom antigo num curso com order bump e a tela "
        "deu erro genérico sem explicar o motivo."
    ),
    "Personalizado (Digite seu próprio relato)": "",
}