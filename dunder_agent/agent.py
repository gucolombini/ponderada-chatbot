from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_transactions import retriever as transactions_retriever
from vector_compliance import retriever as compliance_retriever
from vector_compliance import sanctions as compliance_sanctions
from vector_emails import retriever as emails_retriever
from pipeline import retrieve_fraud, retrieve_conspiracy
from router import retrieve as router_retrieve


load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    max_retries=2,
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

template = """
Você é um assistente virtual que deve responder perguntas relacionadas à empresa.
A Dunder Mifflin ("A Empresa") preza por um ambiente de trabalho profissional, livre de distrações, brincadeiras perigosas e fraudes financeiras.
O dinheiro da empresa deve ser utilizado estritamente para fins comerciais: a venda de papel e produtos de escritório.
Você pode receber algumas transações bancárias, políticas de conformidade ou até emails de funcionários para ajudá-lo a responder. Especifique qual política, transação ou email você está usando para fundamentar sua resposta (se houver, senão ignore).
Especifique os IDs de transações caso usar.
Se a pergunta for sobre fraude, você pode tentar correlacionar as transações e os emails. Leve os a sério.
Providencie uma resposta clara e concisa para o usuário com base nas informações acima.
Não gaste muitos tokens, eles custam caro!

Pergunta do usuário: {question}
Transações possivelmente relevantes: {transactions}
Políticas de conformidade possivelmente relevantes: {compliance}
Sanções possivelmente relevantes: {sanctions}
Emails possivelmente relevantes: {emails}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model
print("Olá, eu sou o Dunder Agent, e estou aqui para te ajudar com qualquer dúvida ou questão que você tiver sobre a empresa!")


while True:
    question = input("(DUNDER AGENT) Faça sua pergunta (ou 'q' para sair): ")
    if question.lower() == 'q':
        break
    
    router_decision = router_retrieve(question)

    transactions = "Nenhuma"
    compliance = "Nenhuma"
    sanctions = "Nenhuma"
    emails = "Nenhum"

    if (router_decision) == "fail":
        print("Routing failed. Please try again.")
        continue

    if router_decision["needs_fraud"]:
        response = retrieve_fraud(question)
        compliance = response["compliance"]
        transactions = response["transactions"]
        emails = response["emails"]
    elif router_decision["needs_conspiracy"]:
        response = retrieve_conspiracy(question)
        compliance = response["compliance"]
        emails = response["emails"]

    else: 
        if router_decision["needs_compliance"]:
            compliance = compliance_retriever(question, 3)
        if router_decision["needs_transactions"]:
            transactions = transactions_retriever(question, 10)
        if router_decision["needs_sanctions"]:
            sanctions = compliance_sanctions
        if router_decision["needs_emails"]:
            emails = emails_retriever(question, 3)
        

    result = chain.invoke({"question": question, "transactions": transactions, "compliance": compliance, "sanctions": sanctions, "emails": emails})
    print("\n" + result.content)
