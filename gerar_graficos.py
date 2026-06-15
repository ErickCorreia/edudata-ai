import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuração do estilo visual dos gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['figure.dpi'] = 300

arquivo_resultado = "resultado_cruzamento_final.xlsx"

print("Carregando os dados para geração dos gráficos...")
try:
    df = pd.read_excel(arquivo_resultado)
except FileNotFoundError:
    print(f"Erro: O arquivo '{arquivo_resultado}' não foi encontrado. Execute o cruzamento primeiro.")
    exit()

if df.empty:
    print("A planilha está vazia. Não há dados para gerar gráficos.")
    exit()

# ---- GRÁFICO 1: APROVAÇÕES POR UNIDADE ----
print("Gerando gráfico de aprovações por unidade...")
plt.figure()

# Conta e ordena os dados
dados_unidade = df['Unidade Escolar'].value_counts()
ax1 = sns.barplot(x=dados_unidade.values, y=dados_unidade.index, palette="Blues_r")

# Adiciona os números em cima de cada barra
for i, v in enumerate(dados_unidade.values):
    ax1.text(v + 0.5, i, str(v), va='center', fontweight='bold', fontsize=10)

plt.title("Total de Alunos Aprovados por Unidade Escolar", fontsize=14, pad=15, fontweight='bold')
plt.xlabel("Quantidade de Aprovados", fontsize=11)
plt.ylabel("Unidade", fontsize=11)
plt.tight_layout()

# Salva a imagem na pasta
nome_grafico_unidade = "grafico_aprovados_por_unidade.png"
plt.savefig(nome_grafico_unidade)
print(f"[✓] Gráfico de unidades salvo como: '{nome_grafico_unidade}'")


# ---- GRÁFICO 2: TOP 10 CURSOS COM MAIS APROVADOS ----
print("Gerando gráfico dos top 10 cursos...")
plt.figure()

# Pega apenas os 10 primeiros cursos com maior volume
dados_cursos = df['Curso Aprovado'].value_counts().head(10)
ax2 = sns.barplot(x=dados_cursos.values, y=dados_cursos.index, palette="viridis")

# Adiciona os números em cima de cada barra
for i, v in enumerate(dados_cursos.values):
    ax2.text(v + 0.2, i, str(v), va='center', fontweight='bold', fontsize=10)

plt.title("Top 10 Cursos com Maior Número de Aprovados", fontsize=14, pad=15, fontweight='bold')
plt.xlabel("Quantidade de Aprovados", fontsize=11)
plt.ylabel("Curso / Carreira", fontsize=11)
plt.tight_layout()

# Salva a imagem na pasta
nome_grafico_cursos = "grafico_top_10_cursos.png"
plt.savefig(nome_grafico_cursos)
print(f"[✓] Gráfico de cursos salvo como: '{nome_grafico_cursos}'")

print("\n=== TODOS OS GRÁFICOS FORAM GERADOS COM SUCESSO ===")
print("Verifique os novos arquivos de imagem (.png) criados na pasta do seu projeto.")
