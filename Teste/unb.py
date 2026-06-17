import pypdf
import re
import pandas as pd

def extrair_dados_unb(caminho_pdf):
    # O Regex ignora quebras de linha falsas e isola o candidato até encontrar um Campus válido
    padrao_unb = re.compile(
        r'([A-Za-zÀ-ÿ\s\-\.\']+?)\s+(\d{8})\s+(.*?(?:Campus Darcy Ribeiro|Campus UnB Ceilândia \(FCE\)|Campus UnB Gama \(FGA\)|Campus UnB Planaltina \(FUP\)))', 
        re.IGNORECASE
    )
    
    dados_extraidos = []
    print(f"Iniciando leitura em bloco do arquivo: {caminho_pdf}")
    
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = pypdf.PdfReader(arquivo)
            
            for num_pagina, pagina in enumerate(leitor.pages):
                try:
                    texto = pagina.extract_text()
                    if not texto: continue
                    
                    # Achata a página inteira: Remove quebras de linha para unir nomes e cursos partidos
                    texto_limpo = texto.replace('\n', ' ')
                    texto_limpo = re.sub(r'\s+', ' ', texto_limpo) 
                    
                    # Limpeza preventiva dos cabeçalhos da tabela do edital
                    texto_limpo = re.sub(r'Nome do candidato Número de inscrição Curso/turno/Campus', '', texto_limpo, flags=re.IGNORECASE)
                    texto_limpo = re.sub(r'UNIVERSIDADE DE BRASÍLIA.*?Curso/turno/Campus', '', texto_limpo, flags=re.IGNORECASE)
                    
                    for match in padrao_unb.finditer(texto_limpo):
                        # Pega o nome e limpa possíveis números soltos de rodapé que se juntaram
                        nome_cru = match.group(1).strip()
                        nome = re.sub(r'^\d+\s+', '', nome_cru) 
                        
                        inscricao = match.group(2).strip()
                        detalhes_curso = match.group(3).strip()
                        
                        # Corta da direita para a esquerda usando rsplit para não afetar cursos com "/" no nome
                        partes = [p.strip() for p in detalhes_curso.rsplit('/', 2)]
                        
                        # SOLUÇÃO APLICADA: Desempacotamento do Python!
                        # Não usamos colchetes, evitando falhas na leitura e no Pandas.
                        if len(partes) == 3:
                            curso, turno, campus = partes
                        else:
                            curso = detalhes_curso
                            turno = "Não informado"
                            campus = "Não informado"
                            
                        dados_extraidos.append({
                            "Nome do Candidato": nome,
                            "Inscrição": inscricao,
                            "Curso": curso,
                            "Turno": turno,
                            "Campus": campus
                        })
                        
                except Exception as e:
                    print(f"Aviso: Falha na leitura da página {num_pagina + 1}. Detalhe: {e}")
                    continue
                            
        # Converte em DataFrame e remove duplicatas
        df_unb = pd.DataFrame(dados_extraidos)
        df_unb = df_unb.drop_duplicates()
        return df_unb

    except Exception as e:
        print(f"Ocorreu um erro crítico na execução: {e}")
        return None

if __name__ == "__main__":
    arquivo_alvo = "ED_18_2024_UNB_VEST_TRADICIONAL_CONV_RA_1_CHAMADA.pdf"
    print("Executando módulo de extração (Motor Blindado Cebraspe)...")
    
    df_resultado = extrair_dados_unb(arquivo_alvo)
    
    if df_resultado is not None and not df_resultado.empty:
        print(f"\nExtração concluída com precisão! Total: {len(df_resultado)} alunos extraídos.")
        print("\nAmostra dos dados limpos:")
        print(df_resultado.head())
        
        nome_arquivo_saida = "base_limpa_unb_2024.xlsx"
        df_resultado.to_excel(nome_arquivo_saida, index=False)
        print(f"\nDados consolidados salvos para o motor IA em: {nome_arquivo_saida}")
    else:
        print("\nFalha na extração ou nenhum candidato encontrado.")