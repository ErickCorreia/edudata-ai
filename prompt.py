import pypdf
import pandas as pd
import re

# 1. Configuração dos caminhos dos arquivos
arquivo_aprovados_pdf = "Vestibular 2026 - 2 Uberlandia Lista de Classificados.pdf" 
arquivo_matriculados_excel = "matriculados_extraido.xlsx"

print("Lendo a planilha de matriculados anterior...")
df_matriculados = pd.read_excel(arquivo_matriculados_excel)

print("Iniciando a leitura e extração do PDF de Aprovados...")
aprovados_lista = []
curso_atual = "Não Identificado"

# 2. Lê o PDF de aprovados e extrai os dados linha por linha
with open(arquivo_aprovados_pdf, "rb") as arquivo:
    leitor = pypdf.PdfReader(arquivo)
    total_paginas = len(leitor.pages)
    print(f"O PDF de aprovados possui {total_paginas} páginas. Processando...")

    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            for linha in texto.split("\n"):
                linha_limpa = linha.strip()
                
                if "Lista de Classificados" in linha_limpa:
                    continue
                if "Concurso Seletivo" in linha_limpa or "UNIVERSIDADE" in linha_limpa:
                    continue
                if "Inscrição Nome EB Concorre" in linha_limpa:
                    continue
                
                if " - " in linha_limpa and not linha_limpa.isdigit() and len(linha_limpa) > 15:
                    curso_atual = linha_limpa
                    continue

                if re.match(r'^\d{8,}', linha_limpa):
                    partes = linha_limpa.split()
                    inscricao = partes[0]
                    
                    palavras_nome = [p for p in partes[1:] if p.isupper() and p not in ["AC", "LI_EP", "LI_PPI", "LB_EP", "LB_PPI", "LB_PCD"]]
                    nome_completo = " ".join(palavras_nome)
                    
                    if nome_completo:
                        aprovados_lista.append({
                            "Inscricao_Vestibular": inscricao,
                            "Nome_Aprovado": nome_completo,
                            "Curso": curso_atual,
                            "Linha_Original_Vestibular": linha_limpa
                        })

df_aprovados = pd.DataFrame(aprovados_lista)
print(f"Sucesso! Extraímos {len(df_aprovados)} alunos aprovados do vestibular.")

# 3. Faz o Cruzamento de Dados e Extração Dinâmica da Unidade
print("Cruzando as duas listas e identificando as unidades...")

df_aprovados['Nome_Busca'] = df_aprovados['Nome_Aprovado'].str.upper()
df_matriculados['Texto_Busca'] = df_matriculados['Texto_Completo'].str.upper()

alunos_encontrados = []

for _, linha_aprovado in df_aprovados.iterrows():
    nome = linha_aprovado['Nome_Busca']
    
    correspondencias = df_matriculados[df_matriculados['Texto_Busca'].str.contains(nome, regex=False, na=False)]
    
    if not correspondencias.empty:
        for _, linha_matr in correspondencias.iterrows():
            texto_matr_original = str(linha_matr['Texto_Completo'])
            texto_matr_upper = texto_matr_original.upper()
            
            # LÓGICA DINÂMICA DE EXTRAÇÃO DE UNIDADE:
            # Procura a palavra OLIMPO e tenta capturar a sigla/palavra que vem logo em seguida
            match_unidade = re.search(r'\bOLIMPO\s+([A-Z0-9ªºáéíóúâêîôûãõç\-_]+)', texto_matr_upper)
            
            if match_unidade:
                termo_unidade = match_unidade.group(1).strip()
                # Padroniza a sigla AC para ficar legível como Águas Claras
                unidade = "Águas Claras" if termo_unidade == "AC" else f"Olimpo {termo_unidade.capitalize()}"
            else:
                # Caso não ache a palavra "Olimpo" na linha, tenta buscar termos geográficos comuns
                if "AGUAS CLARAS" in texto_matr_upper:
                    unidade = "Águas Claras"
                elif "UBERLANDIA" in texto_matr_upper or "UDI" in texto_matr_upper:
                    unidade = "Uberlândia"
                elif "GOIANIA" in texto_matr_upper or "GYN" in texto_matr_upper:
                    unidade = "Goiânia"
                else:
                    unidade = "Não Identificada"
            
            alunos_encontrados.append({
                "Inscrição Vestibular": linha_aprovado['Inscricao_Vestibular'],
                "Nome do Aluno": linha_aprovado['Nome_Aprovado'],
                "Unidade Escolar": unidade,
                "Curso Aprovado": linha_aprovado['Curso'],
                "Dados no Vestibular": linha_aprovado['Linha_Original_Vestibular'],
                "Página no PDF de Matrículas": linha_matr['Pagina'],
                "Dados na Matrícula": texto_matr_original
            })

# 4. Salva o resultado final em um novo arquivo Excel
df_resultado = pd.DataFrame(alunos_encontrados)
# Remove duplicados caso o mesmo aluno gere múltiplas linhas parecidas
if not df_resultado.empty:
    df_resultado = df_resultado.drop_duplicates(subset=["Inscrição Vestibular", "Nome do Aluno"])

arquivo_final = "resultado_cruzamento_final.xlsx"
df_resultado.to_excel(arquivo_final, index=False)

print(f"\n=== CRUZAMENTO CONCLUÍDO COM SUCESSO ===")
print(f"Foram encontrados {len(df_resultado)} alunos matriculados que passaram no vestibular!")
print(f"A planilha pronta foi salva em: '{arquivo_final}'")
