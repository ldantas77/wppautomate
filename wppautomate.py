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
        texto = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8')
        return texto.lower().strip()
    except:
        return str(texto).lower().strip()

# Função para limpar valores nulos do Excel (transforma NaN em texto vazio)
def limpar_valor(valor):
    if pd.isna(valor):
        return ""
    # Se for um número (ex: idade) terminado em .0, remove o .0
    val_str = str(valor).strip()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str

st.markdown("### 💡 Como montar suas mensagens")
st.info(
    "Use as chaves `{ }` para inserir os dados da planilha no meio do texto. "
    "O sistema vai trocar automaticamente pelas informações de cada cliente.\n\n"
    "**Variáveis disponíveis:** `{modelo}`, `{responsavel}`, `{seletiva}`, `{idade}`"
)

# 1. Upload do Arquivo
st.header("1. Upload da Planilha Excel")
uploaded_file = st.file_uploader("Suba seu arquivo (.xlsx ou .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = [normalizar_texto(col) for col in df.columns]
    
    col_telefone = 'telefone 1' if 'telefone 1' in df.columns else 'telefone'
    colunas_necessarias = ['id', 'tipo de lead', 'modelo', col_telefone]
    
    if all(col in df.columns for col in colunas_necessarias):
        st.success("Planilha carregada e lida com sucesso!")
        
        tipos_unicos = df['tipo de lead'].dropna().unique()
        
        # 2. Mensagens Dinâmicas por Tipo
        st.header("2. Textos por Tipo de Lead")
        
        templates_mensagens = {}
        for tipo in tipos_unicos:
            if pd.isna(tipo) or str(tipo).strip() == "":
                continue
            
            # Se for do tipo 'baby', já preenchemos com o seu exemplo exato
            if tipo.lower() == 'baby':
                texto_padrao = (
                    "Olá boa tarde 😊\n"
                    "Falo com a responsável pela {modelo}?\n\n"
                    "Me chamo Jessica, sou do setor de seleção de Modelos para grandes marcas.\n\n"
                    "Recebemos o cadastro e foi pré-selecionada para um evento de moda que acontecerá aqui em {seletiva}.\n\n"
                    "Estamos com campanhas publicitárias em abertas para as marcas: Caedu, Riachuelo e Brandili, e o cadastro chamou a atenção da nossa equipe para essas oportunidades.\n\n"
                    "Me confirma a idade dela por favor\n\n"
                    "https://www.instagram.com/reel/DceIBD3iVA5/?igsi=NDd2M3pta3ZqbG8="
                )
            else:
                texto_padrao = f"Olá! Gostaria de falar sobre o cadastro de {{modelo}} para a seletiva em {{seletiva}}."
                
            templates_mensagens[tipo] = st.text_area(
                f"Mensagem para o lead tipo '{tipo}':", 
                value=texto_padrao,
                height=300
            )
        
        # 3. Processamento e Geração de Links
        st.header("3. Gerar Links de Contato")
        if st.button("Processar Contatos"):
            st.write("### Lista Pronta para Envio")
            
            for index, row in df.iterrows():
                tipo_lead = str(row['tipo de lead']).strip()
                
                if pd.isna(row['tipo de lead']) or pd.isna(row[col_telefone]):
                    continue
                    
                telefone_puro = str(row[col_telefone]).split('.')[0]
                telefone = telefone_puro.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                
                # Pegar os dados da linha (usando a função para evitar que imprima "nan")
                modelo = limpar_valor(row.get('modelo', ''))
                responsavel = limpar_valor(row.get('responsavel', ''))
                seletiva = limpar_valor(row.get('seletiva', ''))
                idade = limpar_valor(row.get('idade', ''))
                
                # Pegar o template escolhido e substituir as variáveis
                mensagem_bruta = templates_mensagens.get(tipo_lead, "")
                
                mensagem_final = mensagem_bruta.replace("{modelo}", modelo) \
                                               .replace("{responsavel}", responsavel) \
                                               .replace("{seletiva}", seletiva) \
                                               .replace("{idade}", idade)
                
                texto_url = urllib.parse.quote(mensagem_final)
                
                if len(telefone) >= 10 and not telefone.startswith("55"):
                    telefone = "55" + telefone
                    
                link_wa = f"https://wa.me/{telefone}?text={texto_url}"
                
                st.markdown(f"**{modelo}** ({tipo_lead}) - Tel: {telefone}")
                st.markdown(f"[👉 Abrir conversa no WhatsApp]({link_wa})")
                st.divider()
                
    else:
        st.error(f"Faltam colunas na planilha. O sistema procurou por: {', '.join(colunas_necessarias)}")
