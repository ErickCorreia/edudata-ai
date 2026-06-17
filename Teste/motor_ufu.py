import pypdf
import re
import pandas as pd
import unicodedata
import os

def padronizar_nome(nome):
    """Normaliza strings para cruzamento cego (sem acentos e em maiúsculo)."""
    if not isinstance(nome, str): return ""
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    return nome.strip().upper()

def extrair_dados_pdf_ufu(caminho_pdf):
    print(f"Iniciando leitura do edital oficial UFU: {caminho_pdf}")
    if not os.path.exists(caminho_pdf):
        print(f"[ERRO FATAL] O arquivo {caminho_pdf} não foi encontrado.")
        return None

    # Regex focado em capturar as cadeias de caracteres do edital
    padrao_ufu = re.compile(r'([A-ZÀ-Ÿ\s]+)', re.IGNORECASE) 
    
    candidatos = []
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = pypdf.PdfReader(arquivo)
            for pagina in leitor.pages:
                texto = pagina.extract_text()
                if texto:
                    for linha in texto.split('\n'):
                        if len(linha.strip()) > 5:
                            candidatos.append({"Texto_Bruto_PDF": linha.strip()})
                            
        return pd.DataFrame(candidatos).drop_duplicates()
    except Exception as e:
        print(f"Falha crítica na leitura do PDF: {e}")
        return None

def executar_analise_ufu(arquivo_excel, arquivo_pdf):
    print(f"Carregando a base interna: {arquivo_excel}")
    if not os.path.exists(arquivo_excel):
        print(f"[ERRO FATAL] Arquivo {arquivo_excel} não está na mesma pasta.")
        return
        
    try:
        df_interno = pd.read_excel(arquivo_excel)
        
         # Identifica dinamicamente a coluna buscando por "nome", "aluno" ou "candidato"
        colunas_com_nome = [col for col in df_interno.columns if any(palavra in str(col).lower() for palavra in ['nome', 'aluno', 'candidato'])]
        
        if not colunas_com_nome:
            # Emite um log de diagnóstico mostrando quais colunas o Excel realmente tem
            print(f"[ERRO FATAL] Coluna de identificação não encontrada. As colunas lidas no Excel foram: {list(df_interno.columns)}")
            return
            
        # BLINDAGEM: Usamos next() iterador para pegar a coluna de forma blindada, sem usar colchetes
        nome_col = next(iter(colunas_com_nome))
        
        # Garante a conversão para texto puro e aplica a padronização
        df_interno['Chave_Cruzamento'] = df_interno[nome_col].astype(str).apply(padronizar_nome)
    except Exception as e:
        print(f"Erro ao processar o arquivo Excel: {e}")
        return

    df_oficial = extrair_dados_pdf_ufu(arquivo_pdf)
    if df_oficial is None or df_oficial.empty:
        return

    print("\nIniciando o cruzamento e auditoria de dados...")
    df_oficial['Chave_Cruzamento'] = df_oficial['Texto_Bruto_PDF'].astype(str).apply(padronizar_nome)
    
    aprovados_confirmados = []
    for _, linha_interna in df_interno.iterrows():
        # Força o dado a ser tratado como String sem vazamento de tipo numérico/float
        nome_aluno = str(linha_interna['Chave_Cruzamento']).strip()
        
        # Pula alunos corrompidos ou vazios
        if nome_aluno == 'NAN' or not nome_aluno:
            continue
            
        # Busca correspondência exata ou contida no edital
        match = df_oficial[df_oficial['Chave_Cruzamento'].str.contains(nome_aluno, na=False, regex=False)]
        
        if not match.empty:
            resultado = linha_interna.to_dict()
            resultado['Status_Auditoria'] = 'APROVADO OFICIAL'
            
            # BLINDAGEM: Iterador substitui o .iloc antigo que gerava falha
            resultado['Registro_Encontrado_PDF'] = next(iter(match['Texto_Bruto_PDF']))
            aprovados_confirmados.append(resultado)

    # Exportação e consolidação
    df_final = pd.DataFrame(aprovados_confirmados)
    if not df_final.empty:
        nome_saida = "Relatorio_Auditoria_UFU_2025.xlsx"
        df_final.drop(columns=['Chave_Cruzamento'], inplace=True, errors='ignore')
        df_final.to_excel(nome_saida, index=False)
        print(f"\n✅ SUCESSO: {len(df_final)} alunos cruzados e validados na lista oficial da UFU.")
        print(f"Arquivo gerado: {nome_saida}")
    else:
        print("\n⚠️ Nenhum aluno da base interna foi validado no PDF oficial. Verifique os dados.")

if __name__ == "__main__":
    arquivo_planilha = "Aprovados UFU 2025.2_1cham.xlsx"
    arquivo_edital = "Aprovados UFU 2025-2.pdf"
    
    executar_analise_ufu(arquivo_planilha, arquivo_edital)