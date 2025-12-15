from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
import os
import pandas as pd

import re

def parse_document(texto):
    blocos = re.split(r"-{10,}", texto)

    emails = []

    padrao = re.compile(
        r"De:\s*(?P<remetente>.+)\n"
        r"Para:\s*(?P<destinatario>.+)\n"
        r"Data:\s*(?P<data>.+)\n"
        r"Assunto:\s*(?P<assunto>.+)\n"
        r"Mensagem:\n(?P<mensagem>[\s\S]+)",
        re.MULTILINE
    )

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco.startswith("De:"):
            continue

        match = padrao.search(bloco)
        if match:
            email = {
                "remetente": match.group("remetente").strip(),
                "destinatario": match.group("destinatario").strip(),
                "data": match.group("data").strip(),
                "assunto": match.group("assunto").strip(),
                "mensagem": match.group("mensagem").strip(),
            }
            emails.append(email)

    return emails

embeddings = OllamaEmbeddings(model="bge-m3")

db_location = "./faiss_db/emails"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    with open("data/emails.txt", "r", encoding="utf-8") as f:
        text = f.read()

    items = parse_document(text)

    for i in items:

        page_content = f"""
            Título: {i['assunto']}
            De: {i['remetente']}
            Mensagem: {i['mensagem']}
            """.strip()
        print(page_content + "\n")

        document = Document(
            page_content=page_content,
            metadata={
                "titulo": i["assunto"],
                "remetente": i["remetente"],
                "destinatario": i["destinatario"],
                "data": i["data"],
                "assunto": i["assunto"],
                "mensagem": i["mensagem"]
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

print(faiss_load.similarity_search("Existe algum email suspeito sobre uma operação vermelha?", 5))

def retriever(query: str, k: int = 5):
    return faiss_load.similarity_search(query, k)