import pypdf
import re
import pandas as pd
import unicodedata

def padronizar_nome(nome):
    """
    Remove acentos, espaços extras e converte para maiúsculo.
    Fundamental para a auditoria e igualdade de palavras do modelo UFU.
    """
    if not isinstance(nome, str): return ""
    # Normalização Unicode para remover acentuação
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    return nome.strip().upper()

def extrair_base_interna_olimpo(caminho_pdf):
    # Regex adaptada para capturar "Matrícula + NOME DO ALUNO + UnB" do PDF tabular
    padrao_olimpo = re.compile(r'(\d{4,6})\s+([A-ZÀ-Ÿ\s]+?)\s+UnB')
    alunos_olimpo = []
    
    print(f"Processando base interna do colégio: {caminho_pdf}")
    
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = pypdf.PdfReader(arquivo)
            for num_pagina, pagina in enumerate(leitor.pages):
                texto = pagina.extract_text()
                if texto:
                    # Achata o texto para contornar a leitura em blocos do PDF tabular
                    texto_limpo = texto.replace('\n', ' ')
                    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
                    
                    for match in padrao_olimpo.finditer(texto_limpo):
                        matricula = match.group(1).strip()
                        nome = match.group(2).strip()
                        alunos_olimpo.append({
                            "Matrícula Olimpo": matricula, 
                            "Nome Olimpo": nome
                        })
    except Exception as e:
        print(f"Erro crítico na leitura da base Olimpo: {e}")
        return None
        
    df_olimpo = pd.DataFrame(alunos_olimpo).drop_duplicates()
    return df_olimpo

def executar_cruzamento_bi(df_oficial, df_interno):
    print("\nIniciando Motor de Cruzamento (Igualdade de Palavras)...")
    
    # Criar chaves de cruzamento normalizadas para evitar falsos negativos
    df_oficial['Chave_Cruzamento'] = df_oficial['Nome do Candidato'].apply(padronizar_nome)
    df_interno['Chave_Cruzamento'] = df_interno['Nome Olimpo'].apply(padronizar_nome)
    
    # Cruzamento exato (Merge/Inner Join)
    df_resultado = pd.merge(df_oficial, df_interno, on='Chave_Cruzamento', how='inner')
    
    # Limpeza da chave temporária usada apenas pelo motor
    df_resultado = df_resultado.drop(columns=['Chave_Cruzamento', 'Nome Olimpo'])
    
    return df_resultado

if __name__ == "__main__":
    # Caminhos dos arquivos base
    arquivo_interno_olimpo = "C:/Users/ckzin/Desktop/analise_dados.py/Teste/Aprovados UnB - 1cham.pdf"
    arquivo_oficial_unb = "C:/Users/ckzin/Desktop/analise_dados.py/Teste/base_limpa_unb_2024.xlsx"
    
    # Passo 1: Extrair dados internos
    df_olimpo = extrair_base_interna_olimpo(arquivo_interno_olimpo)
    
    if df_olimpo is not None and not df_olimpo.empty:
        print(f"Sucesso: {len(df_olimpo)} registros extraídos do documento interno do Olimpo.")
        
        try:
            # Passo 2: Carregar base limpa gerada no passo anterior
            df_unb = pd.read_excel(arquivo_oficial_unb)
            
            # Passo 3: Cruzar informações
            df_final = executar_cruzamento_bi(df_unb, df_olimpo)
            
            # Passo 4: Exportar resultados para o painel de BI
            nome_arquivo_saida = "resultado_cruzamento_final.xlsx"
            df_final.to_excel(nome_arquivo_saida, index=False)
            
            print(f"\n=======================================================")
            print(f"AUDITORIA CONCLUÍDA! Alunos cruzados e validados: {len(df_final)}")
            print(f"Relatório gerado em: {nome_arquivo_saida}")
            print(f"=======================================================\n")
            print("O arquivo final contém a Matrícula Olimpo associada aos dados oficiais (Curso/Turno/Campus).")
            print("Aguardando próximo comando para enviar os insights ao LM Studio ou gerar gráficos.")
            
        except FileNotFoundError:
            print(f"Erro de dependência: Arquivo {arquivo_oficial_unb} não encontrado. Certifique-se de que a extração da UnB ocorreu na mesma pasta.")
    else:
        print("Falha ao extrair alunos da base do Olimpo.")