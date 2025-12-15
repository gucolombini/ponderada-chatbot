from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
import os
import pandas as pd

import re

def parse_document(text):
    results = []

    # regex para capturar seções
    secao_pattern = re.compile(
        r"=+\n(SEÇÃO\s+\d+:\s+.+?)\n=+\n(.*?)(?=\n=+\nSEÇÃO|\Z)",
        re.S
    )

    # regex para capturar itens dentro da seção
    item_pattern = re.compile(
        r"(\d+\.\d+\.\s+.+?)\n(.*?)(?=\n\d+\.\d+\.|\Z)",
        re.S
    )

    # regex para bullets
    bullet_pattern = re.compile(r"^\s*-\s+(.*)", re.M)

    for secao_match in secao_pattern.finditer(text):
        secao_titulo = secao_match.group(1).strip()
        secao_conteudo = secao_match.group(2)

        for item_match in item_pattern.finditer(secao_conteudo):
            item_titulo = item_match.group(1).strip()
            item_conteudo = item_match.group(2)

            bullets = bullet_pattern.findall(item_conteudo)

            results.append({
                "secao": secao_titulo,
                "titulo": item_titulo,
                "bullets": bullets
            })

    return results

embeddings = OllamaEmbeddings(model="bge-m3")

db_location = "./faiss_db/compliance"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    with open("data/politica_compliance.txt", "r", encoding="utf-8") as f:
        text = f.read()

    items = parse_document(text)

    for i in items:

        page_content = f"""
            título: {i['titulo']}
            """.strip()

        document = Document(
            page_content=page_content,
            metadata={
                "secao": i["secao"],
                "bullets": i["bullets"],
            },
            id=str(i)
        )
        
        print(str(i) + "\n")
        ids.append(str(i))
        documents.append(document)

    print("Saving to "+db_location+"\n")
    faiss_db = FAISS.from_documents(documents, embeddings)
    faiss_db.save_local(db_location)
    print("Saved to "+db_location+"\n")

print("Loading from "+db_location+"\n")
faiss_load = FAISS.load_local(db_location, embeddings, allow_dangerous_deserialization=True)

def retriever(query: str, k: int = 5):
    return faiss_load.similarity_search(query, k)

sanctions = """
Violações a estas políticas resultarão nas seguintes medidas escalonadas:
1. Advertência Verbal (Documentada por Toby).
2. Advertência Escrita ("Write-up") - Três advertências resultam em ação disciplinar.
3. Relatório de Desempenho Negativo enviado a Nova York.
4. "Full Disadulation" (Desadulação Completa - termo revogado, manter apenas Demissão por Justa Causa).

Dúvidas devem ser encaminhadas ao anexo do RH. Por favor, não retire os documentos das pastas plásticas.
"""