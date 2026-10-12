from google import genai
import streamlit as st
import requests

# 1. Nova forma de autenticar (usando Client)
chave_api = str(st.secrets["GEMINI_API_KEY"]).strip()
client = genai.Client(api_key=chave_api)

# Inicializar o cliente com a nova biblioteca
client = genai.Client(api_key=str(st.secrets["GEMINI_API_KEY"]).strip())

# Ler a chave diretamente dos Secrets
api_key = st.secrets["GEMINI_API_KEY"]

# 2. Configurações da Página
st.set_page_config(page_title="Avaliação Especializada", page_icon="📊")
st.title("Formulário de Análise Online")

# 3. Função para carregar o PDF na memória
@st.cache_resource
def carregar_material_base():
    # Certifique-se de que o PDF tem EXATAMENTE este nome no GitHub
    arquivo = genai.upload_file("Contexto de dados e pesquisas - Energia Tempo e dinheiro.pdf")
    return arquivo

# 4. Interface do Formulário
st.write("Responda às 5 perguntas abaixo para receber sua análise baseada em nossa metodologia:")

nome = st.text_input("Qual é o seu nome?")
email = st.text_input("Qual é o seu e-mail?")
telefone = st.text_input("Qual é o seu telefone / WhatsApp?")

# As 5 perguntas
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
    
    if nome == "" or email == "" or telefone == "":
        st.warning("Por favor, preencha seu nome, e-mail e telefone antes de continuar.")
    else:
        with st.spinner("Analisando suas respostas cruzando com nossa base de conhecimento..."):
            try:
                # Carrega o PDF e o Modelo
                pdf_arquivo = carregar_material_base()
                response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=[pdf_arquivo, prompt]
)
analise = response.text
                
                # O Prompt com as instruções (FECHADO CORRETAMENTE AQUI)
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

                ESTRUTURA DA ANÁLISE:
                ### Análise Individual das Respostas
                (Para CADA UMA das 5 respostas, busque no PDF o insight correspondente e explique).

                ### Análise Geral e Próximos Passos
                (Juntando as 5 respostas, explique o cenário atual do usuário, os impactos e o próximo passo recomendado).
                """
                
                # CHAMA A IA PARA GERAR A RESPOSTA
                resposta = client.models.generate_content([pdf_arquivo, prompt])
                
                # --- ENVIAR PARA O GOOGLE SHEETS ---
                URL_PLANILHA = "https://script.google.com/macros/s/AKfycbwRhtvpb8YYmafslE02GYoxBT1VltO4Sp3wNNb4vfqgzz1EZZxT-FX36QBQrnbqPrQySA/exec"
                
                dados = {
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                    "resp1": resp1,
                    "resp2": resp2,
                    "resp3": resp3,
                    "resp4": resp4,
                    "resp5": resp5,
                    "analise": resposta.text
                }
                
                try:
                    requests.post(URL_PLANILHA, json=dados)
                except:
                    pass # Garante que o usuário veja a resposta mesmo se a planilha falhar
                
                # EXIBE NA TELA PARA O USUÁRIO
                st.success(f"Pronto, {nome}! Aqui está a sua análise:")
                st.markdown(resposta.text)
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar: {e}")
