import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página
st.set_page_config(page_title="Disparador WhatsApp", layout="wide")
st.title("📱 Gestor de Contatos WhatsApp")

# 1. Apresentação (Editável)
st.header("1. Sua Apresentação")
apresentacao = st.text_area(
    "Texto inicial da mensagem:", 
    value="Olá! Aqui é o Leandro Eduardo, tudo bem?", 
    height=80
)

# 2. Upload do Arquivo
st.header("2. Upload da Planilha Excel")
st.markdown("A planilha deve conter as colunas: `ID | Data do cadastro | tipo de lead | responsavel | modelo | telefone`")
uploaded_file = st.file_uploader("Suba seu arquivo (.xlsx ou .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Ler o arquivo
    df = pd.read_excel(uploaded_file)
    
    # Padronizar nomes das colunas para minúsculas para evitar erros de digitação na planilha
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Colunas esperadas
    colunas_necessarias = ['id', 'data do cadastro', 'tipo de lead', 'responsavel', 'modelo', 'telefone']
    
    # Verificar se as colunas existem
    if all(col in df.columns for col in colunas_necessarias):
        st.success("Planilha carregada com sucesso!")
        
        # Identificar todos os tipos de lead únicos na planilha
        tipos_unicos = df['tipo de lead'].dropna().unique()
        
        # 3. Mensagens Dinâmicas por Tipo
        st.header("3. Textos por Tipo de Lead")
        st.write("Edite a mensagem central para cada tipo de lead encontrado na sua planilha:")
        
        templates_mensagens = {}
        for tipo in tipos_unicos:
            templates_mensagens[tipo] = st.text_area(
                f"Mensagem para o lead tipo '{tipo}':", 
                value=f"Gostaria de falar sobre o cadastro do perfil {tipo}."
            )
        
        # 4. Processamento e Geração de Links
        st.header("4. Gerar Links de Contato")
        if st.button("Processar Contatos"):
            st.write("### Lista Pronta para Envio")
            
            for index, row in df.iterrows():
                tipo_lead = str(row['tipo de lead']).strip()
                # Limpar formatação do telefone (remover espaços, traços, parênteses)
                telefone = str(row['telefone']).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                responsavel = str(row['responsavel'])
                modelo = str(row['modelo'])
                
                # Regra dos campos fixos (Baby/Kids vs Outros)
                if tipo_lead.lower() in ['baby', 'kids']:
                    campos_fixos = f"Responsável: {responsavel}\nModelo: {modelo}"
                else:
                    campos_fixos = f"Modelo: {modelo}"
                    
                # Montar a mensagem final juntando as 3 partes
                mensagem_meio = templates_mensagens.get(tipo_lead, "")
                mensagem_final = f"{apresentacao}\n\n{mensagem_meio}\n\n{campos_fixos}"
                
                # Converter o texto para o formato de URL do WhatsApp
                texto_url = urllib.parse.quote(mensagem_final)
                
                # Assumindo números do Brasil (adiciona 55 se o usuário não tiver colocado)
                if not telefone.startswith("55"):
                    telefone = "55" + telefone
                    
                link_wa = f"https://wa.me/{telefone}?text={texto_url}"
                
                # Exibir botão/link na tela
                st.markdown(f"**{modelo}** ({tipo_lead}) - Tel: {telefone}")
                st.markdown(f"[👉 Abrir conversa no WhatsApp]({link_wa})")
                st.divider()
                
    else:
        st.error("As colunas da planilha não batem com o formato exigido. Verifique os nomes das colunas.")

# Informação sobre o Snowflake na barra lateral
st.sidebar.markdown("### ❄️ Integração Snowflake")
st.sidebar.info(
    "Como você possui conta no **Snowflake**, podemos futuramente substituir o uploader de Excel "
    "por uma conexão direta usando `snowflake.connector`. "
    "Isso permitiria puxar os leads diretamente do seu Data Warehouse com um clique."
)
