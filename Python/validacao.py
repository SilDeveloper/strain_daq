import serial
import serial.tools.list_ports
import numpy as np
import csv
import os
import time
from datetime import datetime

# ============================================================
# VALIDAÇÃO OPERACIONAL DO SISTEMA
#
# Este script realiza a validação experimental da curva de
# calibração obtida para o sistema de pesagem.
#
# Para cada massa de referência são realizadas três
# repetições independentes, envolvendo a retirada e o
# reposicionamento da carga sobre o prato de pesagem.
#
# Ao final são calculados:
#
# - média das massas medidas;
# - desvio padrão;
# - erro absoluto;
# - erro relativo.
#
# Os resultados são armazenados em arquivos CSV para
# posterior análise.
# ============================================================

# Parâmetros obtidos na etapa de reprocessamento da calibração
FATOR_CALIBRACAO = 180920.726039
DESLOCAMENTO     = -1003.802109
G = 9.81

massas_validacao = [15, 35, 75, 125, 175, 225, 275, 325]   # gramas
REPETICOES = 3
AMOSTRAS_POR_REPETICAO = 15
ESPERA_SEGUNDOS = 20


def leitura_para_massa(leitura_raw):

    """
    Converte uma leitura RAW em massa estimada (g)
    utilizando os parâmetros obtidos na calibração.
    """

    forca_N = (leitura_raw - DESLOCAMENTO) / FATOR_CALIBRACAO
    return (forca_N / G) * 1000


PASTA_DADOS = "data"
os.makedirs(PASTA_DADOS, exist_ok=True)

timestamp_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
ARQ_BRUTO  = os.path.join(PASTA_DADOS, f"validacao_bruto_{timestamp_execucao}.csv")
ARQ_RESUMO = os.path.join(PASTA_DADOS, f"validacao_resumo_{timestamp_execucao}.csv")


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


def coletar_repeticao(amostras=AMOSTRAS_POR_REPETICAO):
    valores = []
    tentativas = 0
    while len(valores) < amostras and tentativas < amostras * 3:
        linha = arduino.readline().decode('utf-8').strip()
        tentativas += 1
        try:
            valores.append(float(linha))
        except ValueError:
            continue
    if not valores:
        return None
    return float(np.mean(valores))


resultados_por_massa = {}

print("=" * 60)
print("INÍCIO DA VALIDAÇÃO OPERACIONAL")
print("=" * 60)
print(f"Massas: {massas_validacao} g")
print(f"Repetições por massa: {REPETICOES}")
print(f"Espera por repetição: {ESPERA_SEGUNDOS}s")
print("=" * 60)

with open(ARQ_BRUTO, mode='w', newline='', encoding='utf-8') as f_bruto:
    escritor_bruto = csv.writer(f_bruto)
    escritor_bruto.writerow([
        "timestamp", "massa_referencia_g", "repeticao",
        "leitura_raw_media", "massa_medida_g"
    ])

    for massa_ref in massas_validacao:
        print(f"\n--- {massa_ref} g ---")
        medidas = []

        for rep in range(1, REPETICOES + 1):
            print(f"\n  Repetição {rep}/{REPETICOES}")
            input(f"  Retire e recoloque {massa_ref} g no prato, depois pressione ENTER...")

            print(f"  Aguardando {ESPERA_SEGUNDOS}s...", end='', flush=True)
            arduino.flushInput()
            time.sleep(ESPERA_SEGUNDOS)
            print(" coletando...")

            leitura_raw = coletar_repeticao()
            if leitura_raw is None:
                print("  ERRO: sem leitura. Repetição descartada.")
                continue

            massa_medida = leitura_para_massa(leitura_raw)
            medidas.append(massa_medida)

            escritor_bruto.writerow([
                datetime.now().isoformat(), massa_ref, rep,
                f"{leitura_raw:.4f}", f"{massa_medida:.4f}"
            ])
            f_bruto.flush()
            os.fsync(f_bruto.fileno())

            print(f"  -> {massa_medida:.2f} g  (RAW: {leitura_raw:.1f})")

        resultados_por_massa[massa_ref] = medidas

print("\n" + "=" * 60)
print("Coleta finalizada!")
print("=" * 60)

with open(ARQ_RESUMO, mode='w', newline='', encoding='utf-8') as f_resumo:
    escritor_resumo = csv.writer(f_resumo)
    escritor_resumo.writerow([
        "massa_referencia_g", "n_repeticoes", "massa_media_medida_g",
        "desvio_padrao_g", "erro_absoluto_g", "erro_relativo_pct"
    ])

    print("\n===== RESUMO =====")
    print(f"{'Ref (g)':>8} | {'Medido (g)':>10} | {'Desvio (g)':>10} | {'Erro abs (g)':>12} | {'Erro rel (%)':>12}")
    print("-" * 60)

    for massa_ref, medidas in resultados_por_massa.items():
        if not medidas:
            continue
        n = len(medidas)
        media = float(np.mean(medidas))
        desvio = float(np.std(medidas, ddof=1)) if n > 1 else 0.0
        erro_abs = media - massa_ref
        erro_rel = (erro_abs / massa_ref) * 100 if massa_ref != 0 else float('nan')

        print(f"{massa_ref:>8} | {media:>10.2f} | {desvio:>10.3f} | {erro_abs:>12.2f} | {erro_rel:>12.2f}")

        escritor_resumo.writerow([
            massa_ref, n, f"{media:.4f}", f"{desvio:.4f}",
            f"{erro_abs:.4f}", f"{erro_rel:.4f}"
        ])

print(f"\nResumo salvo em: {ARQ_RESUMO}")
arduino.close()
