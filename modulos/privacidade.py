import re


def mascarar_dados_sensiveis(texto: str) -> str:
    """Substitui e-mails, CPFs e tokens por marcadores seguros (LGPD)."""
    texto = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL_OCULTO]", texto)
    texto = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF_OCULTO]", texto)
    texto = re.sub(r"(token=)([a-zA-Z0-9_\-]+)", r"\1[TOKEN_OCULTO]", texto)
    return texto


def mascarar_lista_logs(logs: list[str]) -> list[str]:
    """Aplica o mascaramento LGPD em uma lista inteira de logs."""
    return [mascarar_dados_sensiveis(linha) for linha in logs]