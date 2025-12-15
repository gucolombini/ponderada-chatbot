from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_transactions import retriever as transactions_retriever
from vector_compliance import retriever as compliance_retriever
from vector_compliance import sanctions as compliance_sanctions
from vector_emails import retriever as emails_retriever
from pipeline_conspiracy import retriever as conspiracy_retriever
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
A Dunder Mifflin ("A Empresa") preza por um ambiente de trabalho profissional, livre de distrações, brincadeiras perigosas e fraudes financeiras. Este manual substitui todas as diretrizes anteriores (incluindo o memorando "Vamos nos divertir" distribuído pelo Gerente Regional em 2006). O objetivo destas regras é garantir a solvência financeira da filial de Scranton e evitar processos judiciais.
O dinheiro da empresa deve ser utilizado estritamente para fins comerciais: a venda de papel e produtos de escritório.
Você pode receber algumas transações bancárias, políticas de conformidade ou até emails de funcionários para ajudá-lo a responder. Especifique qual política, transação ou email você está usando para fundamentar sua resposta.
Se as informações recebidas forem insuficientes para responder a pergunta, diga que não foi possível encontrar uma resposta com base na sua pesquisa.
Se a pergunta do usuário não estiver relacionada à empresa, transações bancárias ou políticas de conformidade, informe politicamente que você só pode responder perguntas relacionadas a esses tópicos.
LEVE OS EMAILS MUITO A SÉRIO! ELES SÃO EVIDÊNCIAS IMPORTANTES! Se houverem evidências de atitudes anti-éticas, ilegais ou que violem as políticas da empresa, destaque-as na sua resposta e cite as evidências.

Nome do usuário: {user_name}
Pergunta do usuário: {question}
Transações possivelmente relevantes: {transactions}
Políticas de conformidade possivelmente relevantes: {compliance}
Sanções possivelmente relevantes: {sanctions}
Emails possivelmente relevantes: {emails}

Providencie uma resposta clara e concisa para o usuário com base nas informações acima.
Não gaste muitos tokens, eles custam caro!
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

username = input("Digite seu nome: ")

while True:
    question = input("(DUNDER AGENT) Faça sua pergunta (ou 'q' para sair): ")
    if question.lower() == 'q':
        break

    transactions = []
    compliance = []
    sanctions = []
    emails = []

    router_decision = router_retrieve(question)

    if (router_decision) == "fail":
        print("Roteamento falhou!")

    elif router_decision["requires"] == "compliance":
        compliance = compliance_retriever(router_decision["prompt"], 3)

    elif router_decision["requires"] == "sanctions":
        print("Fetching sanctions info...\n")
        sanctions = compliance_sanctions

    elif router_decision["requires"] == "emails":
        print("Fetching email info...\n")
        emails = emails_retriever(router_decision["prompt"], 3)

    elif router_decision["requires"] == "conspiracy":
        print("CONSPIRACY PIPELINE INITIATED...\n")
        response = conspiracy_retriever(question)
        emails = response["emails"]
        compliance = response["compliance"]
    
    elif router_decision["required"] == "fraud":
        print("FRAUD PIPELINE INITIATED...\n")

    result = chain.invoke({"user_name": username, "question": question, "transactions": transactions, "compliance": compliance, "sanctions": sanctions, "emails": emails})
    print(result)
    print("\n" + result.content)
