import csv
import matplotlib.pyplot as plt


# caminho do arquivo CSV
arquivo = "data/dados_extensometro.csv"


valores = []


# leitura do CSV
with open(arquivo, "r") as f:

    leitor = csv.reader(f)

    for linha in leitor:

        if not linha:
            continue

        if linha[0].startswith("#"):
            continue

        try:
            raw = int(linha[1])
            valores.append(raw)

        except:
            pass


# cria eixo X (número da leitura)
x = list(range(len(valores)))


# gráfico
plt.figure(figsize=(10,5))

plt.plot(x, valores, marker="o")

plt.title("Leitura do Extensômetro (HX711)")
plt.xlabel("Número da leitura")
plt.ylabel("RAW")

plt.grid(True)

plt.show()