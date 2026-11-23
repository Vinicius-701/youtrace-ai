import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer


class BaseConhecimentoRAG:
    """Armazena documentos técnicos e commits no ChromaDB para busca semântica."""

    def __init__(self, documentos: list[dict]) -> None:
        self.cliente = chromadb.Client()
        self.colecao = self.cliente.get_or_create_collection(name="conhecimento_youshop")
        self.vetorizador = TfidfVectorizer(ngram_range=(1, 2))

        textos = [f"{doc['titulo']} {doc['conteudo']}" for doc in documentos]
        vetores = self.vetorizador.fit_transform(textos).toarray().tolist()

        if self.colecao.count() == 0:
            self.colecao.add(
                ids=[doc["id"] for doc in documentos],
                documents=textos,
                embeddings=vetores,
                metadatas=[{"tipo": doc["tipo"], "titulo": doc["titulo"]} for doc in documentos],
            )

    def total_documentos(self) -> int:
        return self.colecao.count()

    def buscar_contexto(self, pergunta: str, quantidade: int = 2) -> list[dict]:
        vetor_pergunta = self.vetorizador.transform([pergunta]).toarray().tolist()
        resultado = self.colecao.query(query_embeddings=vetor_pergunta, n_results=quantidade)

        trechos = []
        for i in range(len(resultado["ids"][0])):
            trechos.append({
                "id": resultado["ids"][0][i],
                "tipo": resultado["metadatas"][0][i]["tipo"],
                "titulo": resultado["metadatas"][0][i]["titulo"],
                "conteudo": resultado["documents"][0][i],
            })
        return trechos