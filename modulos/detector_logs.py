import re
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.neighbors import LocalOutlierFactor

from modulos.privacidade import mascarar_lista_logs


def analisar_anomalias_logs(logs_brutos: list[str]) -> pd.DataFrame:
    """Transforma os logs em vetores e detecta comportamentos anômalos."""
    logs_seguros = mascarar_lista_logs(logs_brutos)
    palavras_por_log = [re.findall(r"[a-zA-Z0-9_=]+", linha.lower()) for linha in logs_seguros]

    modelo_w2v = Word2Vec(
        sentences=palavras_por_log,
        vector_size=24,
        window=4,
        min_count=1,
        workers=1,
        seed=42,
    )

    vetores = []
    for palavras in palavras_por_log:
        lista_vetores = [modelo_w2v.wv[p] for p in palavras if p in modelo_w2v.wv]
        vetores.append(np.mean(lista_vetores, axis=0))

    matriz = np.array(vetores)
    detector = LocalOutlierFactor(n_neighbors=5, contamination=0.22)
    resultado_ml = detector.fit_predict(matriz)
    pontuacoes = -detector.negative_outlier_factor_

    tabela = pd.DataFrame({
        "log_seguro": logs_seguros,
        "pontuacao_anomalia": np.round(pontuacoes, 3),
        "eh_anomalia": [r == -1 for r in resultado_ml],
        "status": ["🚨 ANOMALIA" if r == -1 else "✅ Normal" for r in resultado_ml],
    })
    return tabela