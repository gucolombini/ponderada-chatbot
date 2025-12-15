from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("data/transacoes_bancarias.csv")

embeddings = OllamaEmbeddings(model="bge-m3")

db_location = "./faiss_db/transacoes"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():

        page_content = f"""
            Transação {row['id_transacao']} realizada em {row['data']}.
            funcionario: {row['funcionario']}
            cargo: {row['cargo']}.
            departamento {row['departamento']}.
            Categoria: {row['categoria']}.
            Descrição: {row['descricao']}.
            Valor: R$ {row['valor']}.
            """.strip()

        document = Document(
            page_content=page_content,
            metadata={
                "id_transacao": row["id_transacao"],
                "data": row["data"],
                "funcionario": row["funcionario"],
                "cargo": row["cargo"],
                "descricao": row["descricao"],
                "valor": row["valor"],
                "categoria": row["categoria"],
                "departamento": row["departamento"],
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