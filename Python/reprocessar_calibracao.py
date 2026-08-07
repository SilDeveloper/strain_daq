import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

# ============================================================
# REPROCESSAMENTO DE CALIBRAÇÃO JÁ COLETADA
#
# Em vez de usar a média das 15 leituras de cada ponto (que
# inclui o período de assentamento/creep), este script usa
# só as ÚLTIMAS N leituras de cada ponto — mais próximas do
# valor já estabilizado.
#
# Não precisa do Arduino. Só do CSV bruto já salvo.
# ============================================================

# --- EDITE AQUI: caminho do CSV bruto que você já coletou ---
# Atualize o nome do arquivo conforme o CSV bruto
# que será utilizado no reprocessamento.
ARQUIVO_ENTRADA = "data/calibracao_bruto_2026_x.csv"

# Quantas leituras finais de cada ponto usar (das 15 coletadas)
N_AMOSTRAS_FINAIS = 5

if not os.path.isfile(ARQUIVO_ENTRADA):
    print(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
    print("Edite a variável ARQUIVO_ENTRADA no topo do script.")
    sys.exit(1)

PASTA_DADOS = "data"
timestamp_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
ARQ_RESUMO = os.path.join(PASTA_DADOS, f"calibracao_resumo_REPROCESSADO_{timestamp_execucao}.csv")
ARQ_GRAFICO = os.path.join(PASTA_DADOS, f"curva_calibracao_REPROCESSADO_{timestamp_execucao}.png")


# ------------------------------------------------------------
# PASSO 1 — Ler o CSV bruto e pegar só as últimas N de cada ponto
# ------------------------------------------------------------

df = pd.read_csv(ARQUIVO_ENTRADA)

tail = df.groupby('massa_g').tail(N_AMOSTRAS_FINAIS)
resumo = tail.groupby('massa_g')['leitura_raw'].agg(
    media='mean', desvio='std', n='count'
).reset_index()

print("=== Resumo (últimas {} amostras de cada ponto) ===".format(N_AMOSTRAS_FINAIS))
print(resumo)


# ------------------------------------------------------------
# PASSO 2 — Converter massa para força e fazer a regressão
# ------------------------------------------------------------

massas  = resumo['massa_g'].values.astype(float)
medias  = resumo['media'].values
desvios = resumo['desvio'].fillna(0).values
ns      = resumo['n'].values

forcas = (massas / 1000) * 9.81

inclinacao, deslocamento, correlacao, _, incerteza = stats.linregress(forcas, medias)
qualidade = correlacao ** 2

previsto = inclinacao * forcas + deslocamento
residuos = medias - previsto


# ------------------------------------------------------------
# PASSO 3 — Resultados
# ------------------------------------------------------------

print("\n===== RESULTADO DA CALIBRAÇÃO (REPROCESSADA) =====")
print(f"Amostras finais usadas por ponto: {N_AMOSTRAS_FINAIS} (de 15 coletadas)")
print(f"Fator de calibração (a): {inclinacao:.4f} RAW/N")
print(f"Deslocamento (b):        {deslocamento:.4f} RAW")
print(f"Qualidade R²:             {qualidade:.6f}")
print(f"Incerteza padrão do fator: {incerteza:.6f}")

print(f"\n# # Parâmetros obtidos na calibração reprocessada para utilização nos demais scripts do sistema:")
print(f"FATOR_CALIBRACAO = {inclinacao:.6f}")
print(f"DESLOCAMENTO     = {deslocamento:.6f}")


# ------------------------------------------------------------
# PASSO 4 — Salvar CSV resumo
# ------------------------------------------------------------

resumo_final = pd.DataFrame({
    "massa_g": massas,
    "forca_N": forcas,
    "leitura_media_raw": medias,
    "desvio_padrao_raw": desvios,
    "n_amostras_usadas": ns,
    "leitura_prevista_raw": previsto,
    "residuo_raw": residuos
})
resumo_final.to_csv(ARQ_RESUMO, index=False)
print(f"\nResumo reprocessado salvo em: {ARQ_RESUMO}")


# ------------------------------------------------------------
# PASSO 5 — Gráficos
# ------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True
)

ax1.errorbar(
    forcas, medias, yerr=desvios, fmt='o', color='#185FA5',
    ecolor='#185FA5', elinewidth=1.2, capsize=3, zorder=5,
    label=f'Pontos (média das últimas {N_AMOSTRAS_FINAIS} leituras ± desvio)'
)

x_fit = np.linspace(min(forcas), max(forcas), 100)
y_fit = inclinacao * x_fit + deslocamento
ax1.plot(
    x_fit, y_fit, '--', color='#1D9E75', lw=2,
    label=f'Regressão linear (R² = {qualidade:.6f})'
)

ax1.set_ylabel('Leitura do Arduino (zerada)')
ax1.set_title('Curva de Calibração (Reprocessada) — Célula de Carga GI + HX711')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.axhline(0, color='black', lw=1)
ax2.scatter(forcas, residuos, color='#C0392B', zorder=5, s=40)
ax2.set_xlabel('Força real (N)')
ax2.set_ylabel('Resíduo (RAW)')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(ARQ_GRAFICO, dpi=150, bbox_inches='tight')
plt.show()

print(f"Gráfico salvo como: {ARQ_GRAFICO}")
