import csv
import time


def salvar_csv(caminho, valor):
    """
    Salva uma nova leitura no arquivo CSV.

    Parâmetros:
    caminho -> caminho do arquivo CSV
    valor -> valor RAW lido do sensor
    """

    # registra o tempo da leitura
    timestamp = time.time()

    # abre o arquivo em modo "append"
    # se o arquivo não existir ele será criado automaticamente
    with open(caminho, "a", newline="") as arquivo:

        writer = csv.writer(arquivo)

        # escreve uma nova linha
        writer.writerow([timestamp, valor])


def linha_vazia(caminho):
    """
    Insere uma linha vazia no CSV.
    Usado para separar diferentes séries experimentais.
    """

    with open(caminho, "a", newline="") as arquivo:

        arquivo.write("\n")