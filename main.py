import streamlit as st
import requests
from supabase import create_client


SUPABASE_URL = st.secrets["supabaseurl"]  
SUPABASE_KEY = st.secrets["supabasekey"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_message(message: str):
    url = "https://api.langflow.astra.datastax.com/lf/05508e76-dadd-49b5-855d-2cb85321b8c7/api/v1/run/ba007a4e-22fb-4b97-b364-a0143aec9e38?stream=false"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer AstraCS:{st.secrets['langflow']}"
    }
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "Agent-tNQyS": {},
            "ChatInput-VoA5k": {},
            "AstraDB-MDDvM": {},
            "OpenAIEmbeddings-BO41u": {},
            "RetrieverTool-tfdq4": {},
            "AstraDB-XWcEV": {},
            "OpenAIEmbeddings-6ZkHB": {},
            "RetrieverTool-PYPTu": {},
            "ChatOutput-YlyNM": {}
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            # Extrair o texto da resposta
            data = response.json()
            outputs = data.get("outputs", [])
            if outputs:
                results = outputs[0].get("outputs", [])
                if results:
                    message_text = results[0].get("results", {}).get("message", {}).get("text")
                    return message_text
            return "Não foi possível encontrar o texto na resposta."
        except Exception as e:
            return f"Erro ao processar a resposta: {str(e)}"
    else:
        return {"error": response.text, "status_code": response.status_code}



# Configuração do estado da sessão
if 'page' not in st.session_state:
    st.session_state['page'] = 'main'

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ''

if 'result' not in st.session_state:
    st.session_state['result'] = ''

if 'is_useful' not in st.session_state:
    st.session_state['is_useful'] = None

if 'additional_feedback' not in st.session_state:
    st.session_state['additional_feedback'] = ''

# Função para exibir a página principal
def main_page():
    st.set_page_config(page_title="Avaliação agente de IA PDV Legal", page_icon=":pencil:")

    st.title("Ajude a avaliar a qualidade das respostas do agente de IA PDV Legal")

    user_input = st.text_area("Digite a sua pergunta:", height=200)

    if st.button("Submeter"):
        with st.spinner("Processando..."):
    

            st.session_state['user_input'] = user_input
            st.session_state['result'] = send_message(user_input)
            st.session_state['page'] = 'feedback'
            
            ########################################################


            st.rerun()



# Função para exibir a página de feedback
def feedback_page():
    st.write("Você digitou:", st.session_state['user_input'])
    st.write("Resultado:", st.session_state['result'])
    st.write("### O resultado foi útil?")
    col1, col2 = st.columns(2)

    if col1.button("👍 Sim"):
        st.session_state['is_useful'] = True
        st.session_state['page'] = 'thank_you'
        
        #update_is_useful_feedback(collection_name: str, id_transacao: str, is_useful: bool)
        
        #update_is_useful_feedback("prisma", st.session_state['document_id'], st.session_state['is_useful'])
        st.rerun()

    if col2.button("👎 Não"):
        st.session_state['is_useful'] = False
        #update_is_useful_feedback("prisma", st.session_state['document_id'], st.session_state['is_useful'])
        st.rerun()

    if st.session_state['is_useful'] == False:
        additional_feedback = st.text_area("Por favor, nos diga como podemos melhorar:")
        if st.button("Enviar Feedback"):
            st.session_state['additional_feedback'] = additional_feedback
            
            #update_feedback_txt("prisma",
            #                    st.session_state['document_id'],
            #                      st.session_state['additional_feedback'])
            st.session_state['page'] = 'thank_you'
            st.rerun()

# Função para exibir a página de agradecimento
def thank_you_page():
    if st.session_state['is_useful'] == True:
        st.write("Obrigado pelo feedback! 👍")
    elif st.session_state['is_useful'] == False:
        st.write("Obrigado pelo feedback! 👎")
        st.write("Seu feedback adicional:", st.session_state['additional_feedback'])

    if st.button("Voltar"):
        st.session_state['page'] = 'main'
        st.session_state['is_useful'] = None
        st.rerun()

# Roteamento das páginas
if st.session_state['page'] == 'main':
    main_page()
elif st.session_state['page'] == 'feedback':
    feedback_page()
elif st.session_state['page'] == 'thank_you':
    thank_you_page()