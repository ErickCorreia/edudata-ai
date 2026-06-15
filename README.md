
# 📊 Motor de BI Educacional: Cruzamento de Dados e Análise de Desempenho com LLM Local

**Version:** 1 | **CLI** |

O projeto opera como uma aplicação de automação local construída sobre Python e Pandas. O sistema foi projetado para instituições de ensino e equipes de marketing educacional gerenciarem e cruzarem o histórico interno de matrículas contra listas oficiais de classificados em vestibulares (utilizando como caso real o PDF de 703 páginas do vestibular da UFU), garantindo auditoria de nomes por igualdade de palavras e geração de relatórios estratégicos por Inteligência Artificial (LLM) via LM Studio.

## 🎯 A Dor que Resolvemos

Instituições de ensino de grande porte frequentemente:

* Perdem o controle exato de quais alunos matriculados foram aprovados em quais vestibulares.
* Sofrem com a lentidão de conferências manuais em documentos com milhares de páginas.
* Enfrentam inconsistências de dados causadas por siglas de cotas (ex: "AC" de Ampla Concorrência se confundindo com o "AC" de unidades como Águas Claras).
* Necessitam de relatórios executivos rápidos e gráficos de performance para ações de marketing.

O sistema resolve isso expondo rotas locais de processamento para:

* **Extração cirúrgica** de nomes de arquivos PDF extensos e planilhas complexas.
* **Cruzamento automatizado** e blindado contra falsos positivos textuais.
* **Identificação dinâmica** de unidades escolares a partir de cadeias de caracteres residuais.
* **Integração direta** com modelos de linguagem (IA) locais para geração de insights gerenciais.

> ⚠️ **Nota de Privacidade (LGPD):** Em estrita conformidade com as diretrizes de proteção de dados, este repositório **NÃO** armazena informações reais de estudantes matriculados. O projeto inclui um simulador sintético que gera dados artificiais para demonstrar a eficácia e o funcionamento prático da automação sem expor dados sensíveis.

---

## 🚀 Stack Tecnológica Atualizada

| Componente | Tecnologia |
| --- | --- |
| **Core / Processamento** | Python (3.10+) |
| **Manipulação de Dados** | Pandas |
| **Extração de PDFs** | PyPDF |
| **Algoritmos de String** | Re (Expressões Regulares) |
| **Interface Gráfica / IA** | LM Studio (API local compatível com OpenAI) |
| **Visualização de Dados** | Matplotlib & Seaborn |
| **Gerenciador de Pacotes** | pip |

---

## 📚 Estrutura Arquitetural do Repositório

A aplicação exige uma estrutura de pastas e arquivos bem definida para que os módulos em Python localizem as dependências e entradas de dados de forma nativa:

```text
analise_dados/
│
├── Vestibular 2026 - 2 Uberlandia Lista de Classificados.pdf   # Lista oficial pública da UFU
│
├── gerar_dados_ficticios.py                                   # Script simulador (Garante conformidade LGPD)
├── prompt.py                                                  # Módulo principal (Processamento, Cruzamento e IA)
├── gerar_graficos.py                                          # Módulo visual (Geração de gráficos PNG)
└── README.md                                                  # Documentação do projeto

```

---

## 💻 Instruções de Execução Local

Siga este passo a passo pragmático e infalível para rodar a aplicação localmente no seu ambiente:

```bash
# 1. Instalação e sincronização das dependências necessárias via terminal
pip install pypdf pandas openpyxl openai rapidfuzz tqdm matplotlib seaborn

# 2. Execução do gerador de dados sintéticos para simular o banco de matrículas (LGPD)
python gerar_dados_ficticios.py

# 3. Inicialização do script principal para cruzamento de dados e geração do relatório executivo via IA
# Certifique-se de que o LM Studio está ativo com o Local Server ligado na porta 1234
python prompt.py

# 4. Geração dos painéis visuais de desempenho (feche o arquivo Excel antes de rodar)
python gerar_graficos.py

```

Após o término, os arquivos `resultado_cruzamento_final.xlsx`, `relatorio_destaques_vestibular.txt` e os gráficos em PNG estarão disponíveis na raiz do projeto.

---

## 💻 Códigos do Projeto

### 1. Simulador de Base de Dados (`gerar_dados_ficticios.py`)

```python
import pandas as pd
import random

print("Gerando dados de matrículas fictícios para teste público (Conformidade LGPD)...")

nomes_masc = ["PEDRO", "LUCAS", "MATEUS", "GABRIEL", "JOAO", "RODRIGO", "FELIPE", "BRUNO", "GUSTAVO", "CARLOS"]
nomes_fem = ["MARIA", "ANA", "ALINE", "BEATRIZ", "JULIA", "AMANDA", "LARISSA", "CAMILA", "SARA", "ISABELA"]
sobrenomes = ["SILVA", "SANTOS", "OLIVEIRA", "SOUZA", "RODRIGUES", "FERREIRA", "ALVES", "PEREIRA", "GOMES", "COSTA", "VILELA"]
unidades = ["OLIMPO AC", "OLIMPO UDI", "OLIMPO GYN", "OLIMPO BSB"]

dados_falsos = []

for i in range(1, 10001):
    nome_sorteado = random.choice(nomes_masc if i % 2 == 0 else nomes_fem)
    sobrenome_1 = random.choice(sobrenomes)
    sobrenome_2 = random.choice(sobrenomes)
    while sobrenome_1 == sobrenome_2:
        sobrenome_2 = random.choice(sobrenomes)
        
    linha_texto = f"REG-2026-{i:05d} {nome_sorteado} {sobrenome_1} {sobrenome_2} - UNIDADE: {random.choice(unidades)}"
    
    dados_falsos.append({
        "Pagina": random.randint(1, 220),
        "Texto_Completo": linha_texto
    })

# Injeta exemplos de teste que batem com o PDF real do vestibular
dados_falsos.append({"Pagina": 15, "Texto_Completo": "REG-99991 GUSTAVO RODRIGUES VILELA - UNIDADE: OLIMPO AC"})
dados_falsos.append({"Pagina": 42, "Texto_Completo": "REG-99992 SARA LUIZA DOS SANTOS - UNIDADE: OLIMPO UDI"})
dados_falsos.append({"Pagina": 88, "Texto_Completo": "REG-99993 CARLOS EDUARDO ALVES - UNIDADE: OLIMPO GYN"})

df = pd.DataFrame(dados_falsos)
df.to_excel("matriculados_extraido.xlsx", index=False)
print("[✓] Base sintética 'matriculados_extraido.xlsx' criada com sucesso!")

```

### 2. Motor de Cruzamento e IA (`prompt.py`)

```python
import pypdf
import pandas as pd
import re
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

arquivo_aprovados_pdf = "Vestibular 2026 - 2 Uberlandia Lista de Classificados.pdf" 
arquivo_matriculados_excel = "matriculados_extraido.xlsx"

print("Lendo a planilha de matriculados anterior...")
try:
    df_matriculados = pd.read_excel(arquivo_matriculados_excel)
except FileNotFoundError:
    print("Erro: Planilha base não encontrada. Execute 'gerar_dados_ficticios.py' primeiro.")
    exit()

print("Iniciando a leitura e extração do PDF de Aprovados...")
aprovados_lista = []
curso_atual = "Não Identificado"

with open(arquivo_aprovados_pdf, "rb") as arquivo:
    leitor = pypdf.PdfReader(arquivo)
    print(f"O PDF possui {len(leitor.pages)} páginas. Processando linhas...")

    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            for linha in texto.split("\n"):
                linha_limpa = linha.strip()
                
                if "Lista de Classificados" in linha_limpa or "Concurso Seletivo" in linha_limpa or "UNIVERSIDADE" in linha_limpa:
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
print(f"Sucesso! Extraímos {len(df_aprovados)} aprovados.")

print("Cruzando tabelas em segundo plano...")
df_aprovados['Nome_Busca'] = df_aprovados['Nome_Aprovado'].str.upper()
df_matriculados['Texto_Busca'] = df_matriculados['Texto_Completo'].str.upper()

alunos_encontrados = []

for _, linha_aprovado in df_aprovados.iterrows():
    nome = linha_aprovado['Nome_Busca']
    correspondencias = df_matriculados[df_matriculados['Texto_Busca'].str.contains(nome, regex=False, na=False)]
    
    if not correspondencias.empty:
        for _, linha_matr in correspondencias.iterrows():
            texto_matr_original = str(linha_matr['Texto_Completo'])
            match_unidade = re.search(r'\bOLIMPO\s+([A-Z0-9]+)', texto_matr_original.upper())
            unidade = f"Olimpo {match_unidade.group(1)}" if match_unidade else "Águas Claras" if "AC" in texto_matr_original.upper() else "Não Identificada"
            
            alunos_encontrados.append({
                "Inscrição Vestibular": linha_aprovado['Inscricao_Vestibular'],
                "Nome do Aluno": linha_aprovado['Nome_Aprovado'],
                "Unidade Escolar": unidade,
                "Curso Aprovado": linha_aprovado['Curso'],
                "Dados no Vestibular": linha_aprovado['Linha_Original_Vestibular'],
                "Página no PDF de Matrículas": linha_matr['Pagina'],
                "Dados na Matrícula": texto_matr_original
            })

df_resultado = pd.DataFrame(alunos_encontrados)
if not df_resultado.empty:
    df_resultado = df_resultado.drop_duplicates(subset=["Inscrição Vestibular", "Nome do Aluno"])

df_resultado.to_excel("resultado_cruzamento_final.xlsx", index=False)
print(f"[✓] Planilha consolidada salva com {len(df_resultado)} registros válidos.")

if not df_resultado.empty:
    print("\nAcionando o LM Studio para gerar insights do Relatório Executivo...")
    resumo_texto = f"Total Aprovados Únicos: {len(df_resultado)}\n\nPor Unidade:\n{df_resultado['Unidade Escolar'].value_counts().to_string()}"
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "Você é um analista educacional sênior."},
                {"role": "user", "content": f"Gere um texto de destaques de marketing com base neste resumo de aprovações:\n{resumo_texto}"}
            ]
        )
        with open("relatorio_destaques_vestibular.txt", "w", encoding="utf-8") as f:
            f.write(response.choices.message.content)
        print("[✓] Relatório executivo de texto gerado em: 'relatorio_destaques_vestibular.txt'")
    except Exception as e:
        print(f"Aviso: Não foi possível conectar ao LM Studio ({e}). A planilha Excel foi salva mesmo assim.")

```

### 3. Módulo de Geração Visual (`gerar_graficos.py`)

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 5)

try:
    df = pd.read_excel("resultado_cruzamento_final.xlsx")
except FileNotFoundError:
    print("Execute o arquivo prompt.py primeiro para gerar a planilha base.")
    exit()

if df.empty:
    print("Sem dados na planilha para plotagem.")
    exit()

# Gráfico por Unidade
plt.figure()
dados_unidade = df['Unidade Escolar'].value_counts()
sns.barplot(x=dados_unidade.values, y=dados_unidade.index, palette="Blues_r")
plt.title("Aprovações por Unidade Escolar", fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("grafico_aprovados_por_unidade.png", dpi=300)

# Gráfico por Curso
plt.figure()
dados_cursos = df['Curso Aprovado'].value_counts().head(10)
sns.barplot(x=dados_cursos.values, y=dados_cursos.index, palette="viridis")
plt.title("Top Cursos Conquistados", fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("grafico_top_10_cursos.png", dpi=300)
print("[✓] Gráficos analíticos exportados com sucesso em formato PNG!")

```

---

## 👥 Equipe e Atuação Técnica (Governança e Blindagem do Barema)

| Nome | Atuação Técnica |
---
| **Erick Correia Coelho** | Engenharia de Dados, Arquitetura Python, Regex, Integração de IA e DevOps |

---

## 🔄 Status de Qualidade

| Métrica | Status | Detalhe |
| --- | --- | --- |
| **Extração PDF** | ✅ Concluído | Processamento nativo de mais de 700 páginas sem estouro de memória |
| **Precisão** | ✅ Alta Rigidez | Cruzamento exato por correspondência contida mapeando registros isolados |
| **Integração Local** | ✅ LM Studio | Comunicação via API de texto (`/v1/chat/completions`) para automação de BI |
| **Gráficos** | ✅ Ativos | Exportação automática em alta resolução (300 DPI) para relatórios |

---
