from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=50
)

template = """
Você é um agente roteador para um chatbot assistente de uma empresa.

Baseado na pergunta, escolha qual desses deve ser buscado:
- política de conformidade
- sanções (se houver violações)
- busca básica de emails
- pipeline de investigação - fraude
- pipeline de investigação - conspiração
E crie um prompt simples (<10 palavras) para ajudar o próximo agente.

Retorne APENAS json válido nesse formato:
{{
    "requires": "compliance", "sanctions", "fraud", "conspiracy", "emails" ou "none"
    "prompt": "<seu prompt aqui>"
}}

Pergunta: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def retrieve(question: str):
    result = chain.invoke({"question": question})
    print(result.content)

    try: routing = json.loads(result.content)
    except json.JSONDecodeError:
        return "fail"

    requires = routing.get("requires", False)
    prompt = routing.get("prompt", False)
    response = {
        "requires": requires,
        "prompt": prompt
    }

    return response

