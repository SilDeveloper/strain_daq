import serial
import serial.tools.list_ports
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time
import csv
import os
from datetime import datetime

# ============================================================
# CALIBRAÇÃO DO SISTEMA DE PESAGEM
#
# Este script realiza a calibração experimental do sistema
# composto por célula de carga Single Point, módulo HX711
# e Arduino Uno.
#
# Para cada massa de referência são adquiridas 15 leituras
# consecutivas, utilizadas para o cálculo da média e do
# desvio padrão das medições.
#
# Os dados coletados são armazenados em arquivos CSV para
# posterior análise. Ao final do processo são calculados:
#
# - curva de calibração;
# - regressão linear;
# - coeficiente de determinação (R²);
# - resíduos da regressão;
# - parâmetros de conversão RAW → força.
#
# Também é gerado automaticamente um gráfico contendo a
# curva de calibração e a distribuição dos resíduos.
#
# Observação:
# O Arduino realiza a tara automaticamente durante a
# inicialização, de modo que as leituras recebidas já
# estão referenciadas em relação à condição sem carga.
# ============================================================

PASTA_DADOS = "data"
os.makedirs(PASTA_DADOS, exist_ok=True)

timestamp_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
ARQ_BRUTO = os.path.join(PASTA_DADOS, f"calibracao_bruto_{timestamp_execucao}.csv")
ARQ_RESUMO = os.path.join(PASTA_DADOS, f"calibracao_resumo_{timestamp_execucao}.csv")
ARQ_GRAFICO = os.path.join(PASTA_DADOS, f"curva_calibracao_{timestamp_execucao}.png")


# ------------------------------------------------------------
# PASSO 1 — Conectar ao Arduino
# ------------------------------------------------------------

def encontrar_porta():
    portas = serial.tools.list_ports.comports()
    for p in portas:
        if any(x in p.description for x in ['Arduino', 'CH340', 'USB']):
            return p.device
    return None


porta = encontrar_porta()

if porta is None:
    print("Arduino não encontrado automaticamente.")
    for p in serial.tools.list_ports.comports():
        print(f"  {p.device} — {p.description}")
    porta = input("\nDigite a porta manualmente (ex: COM3): ").strip()

print(f"\nConectando em: {porta}")
arduino = serial.Serial(porta, baudrate=9600, timeout=3)

print("Aguardando Arduino inicializar e tarar...", end='', flush=True)
time.sleep(3)
arduino.flushInput()
print(" pronto!\n")


# ------------------------------------------------------------
# PASSO 2 — Coleta de leituras, gravando cada uma no CSV bruto
# ------------------------------------------------------------

def coletar_leitura(peso_g, amostras=15, arquivo_bruto=ARQ_BRUTO):
    """
    Realiza a aquisição de leituras fornecidas pelo Arduino.
    
    Cada valor recebido é armazenado imediatamente em um
    arquivo CSV bruto, permitindo preservar os dados
    experimentais mesmo em caso de interrupção do programa.
    
    Retorna a lista completa de leituras para posterior
    cálculo de média, desvio padrão e análise estatística.
    """
    valores = []
    tentativas = 0

    arquivo_existe = os.path.isfile(arquivo_bruto)
    with open(arquivo_bruto, mode='a', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        if not arquivo_existe:
            escritor.writerow(["timestamp", "massa_g", "leitura_raw"])

        while len(valores) < amostras and tentativas < amostras * 3:
            linha = arduino.readline().decode('utf-8').strip()
            tentativas += 1
            try:
                v = float(linha)
            except ValueError:
                continue

            valores.append(v)
            escritor.writerow([datetime.now().isoformat(), peso_g, v])
            f.flush()
            os.fsync(f.fileno())  # garante gravação física em disco

    return valores


# ------------------------------------------------------------
# PASSO 3 — Sequência de calibração
# ------------------------------------------------------------
# Pesos disponíveis:(ajuste conforme os pesos de referência que você tiver disponíveis)

pesos_gramas = [0, 10, 20, 50, 100, 150, 200, 250, 300, 350]

leituras_coletadas = []  # cada item: (peso, media, desvio, n_amostras)

print("=" * 50)
print("INÍCIO DA CALIBRAÇÃO")
print("=" * 50)
print(f"Dados brutos serão salvos em: {ARQ_BRUTO}")
print("Para cada passo:")
print("  1. Monte o peso indicado no centro do prato")
print("  2. Aguarde 5 segundos para estabilizar")
print("  3. Pressione ENTER para registrar")
print("=" * 50)

for peso in pesos_gramas:
    if peso == 0:
        print(f"\n[Passo] Retire TODOS os pesos do prato (0g)")
    else:
        print(f"\n[Passo] Coloque {peso}g no centro do prato")

    input("  Pressione ENTER quando estiver pronto...")

    print("  Aguardando estabilização (5s)...", end='', flush=True)
    time.sleep(5)
    arduino.flushInput()
    print(" coletando...")

    valores = coletar_leitura(peso, amostras=15)

    if not valores:
        print("  ERRO: não foi possível ler o Arduino. Pulando esse ponto.")
        continue

    media = float(np.mean(valores))
    desvio = float(np.std(valores, ddof=1)) if len(valores) > 1 else 0.0
    n = len(valores)

    leituras_coletadas.append((peso, media, desvio, n))
    print(f"  -> {peso}g = {media:.1f} +/- {desvio:.2f}  (n={n})")

print("\n" + "=" * 50)
print("Coleta finalizada!")
print(f"Leituras brutas salvas em: {ARQ_BRUTO}")
print("=" * 50)


# ------------------------------------------------------------
# PASSO 4 — Converter massa para força
# ------------------------------------------------------------

massas  = np.array([p for p, _, _, _ in leituras_coletadas])
medias  = np.array([m for _, m, _, _ in leituras_coletadas])
desvios = np.array([d for _, _, d, _ in leituras_coletadas])
ns      = np.array([n for _, _, _, n in leituras_coletadas])

# Força em Newtons: F = (massa em kg) x 9,81
forcas = (massas / 1000) * 9.81


# ------------------------------------------------------------
# PASSO 5 — Regressão linear
# ------------------------------------------------------------
# Como a tara é realizada automaticamente pelo Arduino,
# espera-se que o intercepto permaneça próximo de zero.
# Pequenos desvios podem ocorrer em função de efeitos
# térmicos, ruídos elétricos ou acomodação mecânica.

inclinacao, deslocamento, correlacao, _, incerteza = stats.linregress(
    forcas,  # eixo X - força real em Newtons
    medias   # eixo Y - leitura média do Arduino (já zerada)
)

qualidade = correlacao ** 2


# ------------------------------------------------------------
# PASSO 6 — Resíduos da regressão
# ------------------------------------------------------------

previsto = inclinacao * forcas + deslocamento
residuos = medias - previsto


# ------------------------------------------------------------
# PASSO 7 — Resultados no console
# ------------------------------------------------------------

print("\n===== RESULTADO DA CALIBRAÇÃO =====")
print(f"Fator de calibração (a): {inclinacao:.4f} RAW/N")
print(f"Deslocamento (b):        {deslocamento:.4f} RAW")
print(f"Qualidade R²:             {qualidade:.6f}")
print(f"Incerteza padrão do fator: {incerteza:.6f}")

if qualidade > 0.999:
    print("\n[OK] Calibração excelente - R² acima de 0,999")
elif qualidade > 0.99:
    print("\n[ATENÇÃO] Calibração aceitável - R² entre 0,99 e 0,999")
else:
    print("\n[RUIM] Calibração ruim - verifique a montagem e os pesos")

print(f"\n# Cole isso no main.py e no validacao.py:")
print(f"FATOR_CALIBRACAO = {inclinacao:.6f}")
print(f"DESLOCAMENTO     = {deslocamento:.6f}")


# ------------------------------------------------------------
# PASSO 8 — Salvar CSV resumo (1 linha por ponto de calibração)
# ------------------------------------------------------------

with open(ARQ_RESUMO, mode='w', newline='', encoding='utf-8') as f:
    escritor = csv.writer(f)
    escritor.writerow([
        "massa_g", "forca_N", "leitura_media_raw", "desvio_padrao_raw",
        "n_amostras", "leitura_prevista_raw", "residuo_raw"
    ])
    for i in range(len(massas)):
        escritor.writerow([
            massas[i], f"{forcas[i]:.6f}", f"{medias[i]:.4f}",
            f"{desvios[i]:.4f}", ns[i],
            f"{previsto[i]:.4f}", f"{residuos[i]:.4f}"
        ])

print(f"\nResumo (média, desvio, resíduo por ponto) salvo em: {ARQ_RESUMO}")


# ------------------------------------------------------------
# PASSO 9 — Funções de conversão (reaproveite no validacao.py)
# ------------------------------------------------------------

def leitura_para_forca(leitura):
    """Converte leitura do Arduino em força (N)."""
    return (leitura - deslocamento) / inclinacao


def leitura_para_massa(leitura):
    """Converte leitura do Arduino em massa (g)."""
    return leitura_para_forca(leitura) / 9.81 * 1000


# ------------------------------------------------------------
# PASSO 10 — Gráficos: curva de calibração + resíduos
# ------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True
)

# --- painel 1: curva de calibração com barras de erro ---
ax1.errorbar(
    forcas, medias, yerr=desvios, fmt='o', color='#185FA5',
    ecolor='#185FA5', elinewidth=1.2, capsize=3, zorder=5,
    label='Pontos de calibração (média ± desvio padrão)'
)

x_fit = np.linspace(min(forcas), max(forcas), 100)
y_fit = inclinacao * x_fit + deslocamento
ax1.plot(
    x_fit, y_fit, '--', color='#1D9E75', lw=2,
    label=f'Regressão linear (R² = {qualidade:.6f})'
)

ax1.set_ylabel('Leitura do Arduino (zerada)')
ax1.set_title('Curva de Calibração — Célula de Carga GI + HX711')
ax1.legend()
ax1.grid(alpha=0.3)

# --- painel 2: resíduos da regressão ---
ax2.axhline(0, color='black', lw=1)
ax2.scatter(forcas, residuos, color='#C0392B', zorder=5, s=40)
ax2.set_xlabel('Força real (N)')
ax2.set_ylabel('Resíduo (RAW)')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(ARQ_GRAFICO, dpi=150, bbox_inches='tight')
plt.show()

print(f"\nGráfico salvo como: {ARQ_GRAFICO}")

arduino.close()
