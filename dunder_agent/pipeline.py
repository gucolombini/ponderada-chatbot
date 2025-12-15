from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_transactions import retriever as transactions_retriever
from vector_compliance import retriever as compliance_retriever
from vector_emails import retriever as emails_retriever
import json

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=50
)

template_transaction = """
Você deve construir um prompt para busca de transações ilegítimas em uma Vector Database, construída sobre um simples csv de entradas e saídas.
O prompt deve ser simples e conciso, mas deve ser capaz de encontrar as transações relevantes. "nome funcionário, tipo de transação, destino do dinheiro, etc."
Use informações dos emails para construir o prompt da busca.
Retorne APENAS o prompt, para economizar tokens.

Pergunta original: {question}
Emails encontrados: {emails}
"""

def retrieve_fraud(question: str):
    emails = emails = emails_retriever(question, 3)

    prompt = ChatPromptTemplate.from_template(template_transaction)
    chain = prompt | model
    transaction_prompt = chain.invoke({"question": question, "emails": emails}).content
    print(transaction_prompt)
    transactions = transactions_retriever(transaction_prompt, 5)
    print(transactions)
    compliance = compliance_retriever(question, 1)

    response = {
        "emails": emails,
        "transactions": transactions,
        "compliance": compliance
    }

    return response

def retrieve_conspiracy(question: str):
    emails = emails = emails_retriever(question, 4)
    compliance = compliance_retriever(question, 2)

    response = {
        "emails": emails,
        "compliance": compliance
    }

    return response

