import streamlit as st
import google.generativeai as genai

# 1. Configurações da Página
st.set_page_config(page_title="Diagnóstico Especializado", page_icon="📊")
st.title("Formulário de Diagnóstico em Tempo Real")

# 2. Conecta ao cofre seguro do Streamlit para pegar a chave
# A chave não fica no código para não vazar!
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Função para carregar o PDF na memória (cache para ser rápido)
@st.cache_resource
def carregar_material_base():
    # Substitua "Contexto de dados e pesquisas - Energia Tempo e dinheiro.pdf" pelo nome exato do seu arquivo PDF
    arquivo = genai.upload_file("Contexto de dados e pesquisas - Energia Tempo e dinheiro.pdf")
    return arquivo

# 4. Interface do Formulário
st.write("Responda às 5 perguntas abaixo para receber sua análise baseada em nossa metodologia:")

nome = st.text_input("Qual é o seu nome?")
email = st.text_input("Qual é o seu e-mail?")
telefone = st.text_input("Qual é o seu telefone / WhatsApp?")

# Adapte as perguntas e as alternativas de acordo com o seu negócio
resp1 = st.radio("1. O que mais te incomoda no dia a dia hoje?", 
                 ["Dependência em mim para fazer tudo", "Erros recorrentes e retrabalho", "Falta de processos e perdas financeiras", "Riscos regulatórios"])

resp2 = st.radio("2. Como você classifica esse problema?", 
                 ["Pontual", "Processual", "Setorial", "Generalizado"])

resp3 = st.radio("3. Está disposto a resolver isso agora?", 
                 ["Sim, imediatamente", "Pretendo esperar mais um pouco", "Não pretendo mexer nisso muito cedo"])

resp4 = st.radio("4. Você já possui algum projeto para fazer alguma adequação em relação a essa situação?", 
                 ["Não, mas tenho orçamento", "Não e não tenho orçamento", "Sim, está em andamento", "Sim, mas não foi iniciado"])

resp5 = st.radio("5. Quanto você estima que tem de perdas com essa situação?", 
                 ["Não imagino", "Entre R$1k e R$10k", "Entre R$10k e R$50k", "Acima de R$50k"])

# 5. Botão que aciona a Inteligência Artificial
if st.button("Obter Análise Agora"):
    
    if nome == "":
        st.warning("Por favor, preencha o seu nome antes de continuar.")
    else:
        # Mostra um ícone de carregamento enquanto a IA "pensa"
        with st.spinner("Analisando suas respostas cruzando com nossa base de conhecimento..."):
            try:
                # Carrega o PDF e o Modelo
                pdf_arquivo = carregar_material_base()
                modelo = genai.GenerativeModel("gemini-1.5-flash")
                
                # O Prompt com as instruções
                prompt = f"""
                Você é um consultor especialista e analítico. Em anexo (PDF), está meu material de referência.
                
                O usuário chamado {nome} acabou de responder a um questionário. 
                Respostas:
                1. {resp1}
                2. {resp2}
                3. {resp3}
                4. {resp4}
                5. {resp5}

                Sua tarefa é cruzar essas respostas com o material do PDF e montar um relatório estruturado.

FORMATAÇÃO DA RESPOSTA:
- Use Markdown limpo para estruturar o texto (títulos com ###, destaques em **negrito** e listas em tópicos -).
- NÃO utilize código HTML direto na resposta.

ESTRUTURA DO DIAGNÓSTICO:
### Análise Individual das Respostas
(Para CADA UMA das 5 respostas, busque no PDF o insight correspondente e explique).

### Diagnóstico Geral e Próximos Passos
(Juntando as 5 respostas, explique o cenário atual do usuário, os impactos e o próximo passo recomendado).
"""
