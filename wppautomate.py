import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata

# Configuração da página
st.set_page_config(page_title="Disparador WhatsApp", layout="wide")
st.title("📱 Gestor de Contatos WhatsApp")

# Função para remover acentos e padronizar colunas
def normalizar_texto(texto):
    try:
        # Tira acentos, deixa minúsculo e remove espaços nas pontas
        texto = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8')
        return texto.lower().strip()
    except:
        return str(texto).lower().strip()

# 1. Apresentação
st.header("1. Sua Apresentação")
apresentacao = st.text_area(
    "Texto inicial da mensagem:", 
    value="Olá! Aqui é o Leandro Eduardo da Vale Help Cell, tudo bem?", 
    height=80
)

# 2. Upload do Arquivo
st.header("2. Upload da Planilha Excel")
uploaded_file = st.file_uploader("Suba seu arquivo (.xlsx ou .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Ler o arquivo
    df = pd.read_excel(uploaded_file)
    
    # Padronizar nomes das colunas (tira acentos e maiúsculas)
    df.columns = [normalizar_texto(col) for col in df.columns]
    
    # Mapeamento flexível para encontrar as colunas certas, independente de pequenas variações
    col_telefone = 'telefone 1' if 'telefone 1' in df.columns else 'telefone'
    col_data = 'data do lead' if 'data do lead' in df.columns else 'data do cadastro'
    
    colunas_necessarias = ['id', 'tipo de lead', 'responsavel', 'modelo', col_telefone]
    
    # Verificar se as colunas existem
    if all(col in df.columns for col in colunas_necessarias):
        st.success("Planilha carregada e lida com sucesso!")
        
        # Identificar todos os tipos de lead únicos na planilha (removendo vazios)
        tipos_unicos = df['tipo de lead'].dropna().unique()
        
        # 3. Mensagens Dinâmicas por Tipo
        st.header("3. Textos por Tipo de Lead")
        st.write("Edite a mensagem central para cada tipo de lead encontrado na sua planilha:")
        
        templates_mensagens = {}
        for tipo in tipos_unicos:
            # Pular se o tipo for vazio
            if pd.isna(tipo) or str(tipo).strip() == "":
                continue
                
            templates_mensagens[tipo] = st.text_area(
                f"Mensagem para o lead tipo '{tipo}':", 
                value=f"Gostaria de falar sobre o cadastro do perfil {tipo} que realizou conosco na seletiva."
            )
        
        # 4. Processamento e Geração de Links
        st.header("4. Gerar Links de Contato")
        if st.button("Processar Contatos"):
            st.write("### Lista Pronta para Envio")
            
            for index, row in df.iterrows():
                tipo_lead = str(row['tipo de lead']).strip()
                
                # Pular linhas onde o tipo de lead ou telefone estão vazios
                if pd.isna(row['tipo de lead']) or pd.isna(row[col_telefone]):
                    continue
                    
                telefone_puro = str(row[col_telefone]).split('.')[0] # Evita casos como '1199999999.0'
                telefone = telefone_puro.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                
                responsavel = str(row['responsavel']) if not pd.isna(row['responsavel']) else ""
                modelo = str(row['modelo']) if not pd.isna(row['modelo']) else ""
                
                # Regra dos campos fixos (Baby/Kids vs Outros)
                if tipo_lead.lower() in ['baby', 'kids']:
                    campos_fixos = f"Responsável: {responsavel}\nModelo: {modelo}"
                else:
                    campos_fixos = f"Modelo: {modelo}"
                    
                # Montar a mensagem final
                mensagem_meio = templates_mensagens.get(tipo_lead, "")
                mensagem_final = f"{apresentacao}\n\n{mensagem_meio}\n\n{campos_fixos}"
                
                # Converter para formato de URL
                texto_url = urllib.parse.quote(mensagem_final)
                
                # Adiciona o 55 do Brasil se faltar
                if len(telefone) >= 10 and not telefone.startswith("55"):
                    telefone = "55" + telefone
                    
                link_wa = f"https://wa.me/{telefone}?text={texto_url}"
                
                # Exibir botão/link na tela
                st.markdown(f"**{modelo}** ({tipo_lead}) - Tel: {telefone}")
                st.markdown(f"[👉 Abrir conversa no WhatsApp]({link_wa})")
                st.divider()
                
    else:
        st.error(f"Faltam colunas na planilha. O sistema procurou por: {', '.join(colunas_necessarias)}")
