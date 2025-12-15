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
You are a classifier.

Decide whether the user's question requires:
- bank transaction data
- compliance policy information
- sanctions information (responses for violations of policies)
- email data
- further investigation using one of the pipelines (fraud or conspiracy)

Return ONLY valid JSON in this format:
{{
    "transactions": true/false,
    "compliance": true/false,
    "sanctions": true/false,
    "emails": true/false,
    "fraud": true/false,
    "conspiracy": true/false
}}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def retrieve(question: str):
    result = chain.invoke({"question": question})
    print(result.content)

    try: routing = json.loads(result.content)
    except json.JSONDecodeError:
        return "fail"

    needs_transactions = routing.get("transactions", False)
    needs_compliance = routing.get("compliance", False)
    needs_sanctions = routing.get("sanctions", False)
    needs_emails = routing.get("emails", False)
    needs_fraud = routing.get("fraud", False)
    needs_conspiracy = routing.get("conspiracy", False)
    response = {
        "needs_transactions": needs_transactions,
        "needs_compliance": needs_compliance,
        "needs_sanctions": needs_sanctions,
        "needs_emails": needs_emails,
        "needs_fraud": needs_fraud,
        "needs_conspiracy": needs_conspiracy
    }

    return response

