from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_emails import retriever as emails_retriever
from vector_compliance import retriever as compliance_retriever
import json

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=100
)

template_1 = """
Sintetize em menos de 30 palavras qual a atividade suspeita aqui. Se não houver nada, retorne apenas a palavra "ERROR"

Retorne APENAS a resposta, não gaste tokens

Pergunta original: {question}
Emails: {emails}
"""

prompt = ChatPromptTemplate.from_template(template_1)
chain = prompt | model

def retriever(question: str):
    emails = []
    compliance = []

    emails.append(emails_retriever(question, 3))
    compliance_prompt = chain.invoke({"question": question, "emails": emails}).content
    print(compliance_prompt)

    # Se não houver atividade suspeita, retorna falso.
    if compliance_prompt == "ERROR" or compliance_prompt == "ERROR." or compliance_prompt == '''"ERROR"''' or compliance_prompt == '''"ERROR."''' or compliance_prompt == '''"ERROR".''':
        print("\n\n\n\n\nKYS\n\n\n")
        return False
    
    compliance.append(compliance_retriever(compliance_prompt))

    return {
        "emails": emails,
        "compliance": compliance
    }

