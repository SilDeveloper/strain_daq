import time
import csv
import numpy as np
import matplotlib.pyplot as plt
from acquisition.serial_reader import iniciar_serial, ler_serial

# =========================
# CONFIGURAÇÕES
# =========================
PORTA = "COM3"
BAUDRATE = 9600
AMOSTRAS = 100
ARQUIVO_SAIDA = "data/calibracao.csv"

# =========================
# INICIALIZA SERIAL
# =========================
ser = iniciar_serial(PORTA, BAUDRATE)

print("\n=== CALIBRAÇÃO DO SISTEMA ===\n")

dados = []

# =========================
# FUNÇÃO DE COLETA
# =========================
def coletar_media(n_amostras):
    valores = []

    while len(valores) < n_amostras:
        linha = ler_serial(ser)

        if linha and "RAW" in linha:
            try:
                valor = int(linha.split(":")[-1].strip())

                if valor != 0:
                    valores.append(valor)

            except:
                pass

    media = sum(valores) / len(valores)
    return media

# =========================
# LOOP DE CALIBRAÇÃO
# =========================
while True:

    input("\nColoque uma carga e pressione ENTER...")

    raw_medio = coletar_media(AMOSTRAS)

    massa = float(input("Digite a massa (em gramas): "))

    # converte para Newton
    forca = (massa / 1000) * 9.81

    print(f"RAW médio: {raw_medio:.2f}")
    print(f"Força: {forca:.4f} N")

    dados.append((raw_medio, forca))

    continuar = input("Adicionar outro ponto? (s/n): ")

    if continuar.lower() != "s":
        break

# =========================
# SEPARA DADOS
# =========================
raw_vals = [d[0] for d in dados]
forcas = [d[1] for d in dados]

# =========================
# AJUSTE LINEAR
# =========================
coef = np.polyfit(raw_vals, forcas, 1)
a, b = coef

print("\n=== RESULTADO DA CALIBRAÇÃO ===")
print(f"Força = {a:.6f} * RAW + {b:.6f}")

# =========================
# SALVAR CSV
# =========================
with open(ARQUIVO_SAIDA, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["RAW_medio", "Forca_N"])

    for r, f_ in dados:
        writer.writerow([r, f_])

print(f"\nDados salvos em: {ARQUIVO_SAIDA}")

# =========================
# GRÁFICO
# =========================
plt.figure()

plt.scatter(raw_vals, forcas, label="Dados experimentais")

# reta ajustada
x = np.linspace(min(raw_vals), max(raw_vals), 100)
y = a * x + b

plt.plot(x, y, label="Ajuste linear")

plt.xlabel("RAW")
plt.ylabel("Força (N)")
plt.title("Curva de Calibração")

plt.legend()
plt.grid()

plt.show()