from acquisition.serial_reader import iniciar_serial, ler_serial
from acquisition.csv_logger import salvar_csv, linha_vazia
from collections import deque
import msvcrt

# caminho onde os dados serão armazenados
ARQUIVO = "data/dados_extensometro.csv"

# inicia comunicação com Arduino
ser = iniciar_serial("COM3", 9600)

print("Sistema DAQ iniciado")
print("Pressione ENTER para iniciar aquisição")
print("Pressione ESPAÇO para parar")

input()

print("Aquisição iniciada...")

janela = deque(maxlen=10)

while True:

    linha = ler_serial(ser)

    if linha and "RAW" in linha:

        try:
            valor = int(linha.split(":")[-1].strip())

            if valor != 0:

                janela.append(valor)

                media = sum(janela) / len(janela)

                print(f"RAW bruto: {valor} | filtrado: {media:.2f}")

                salvar_csv(ARQUIVO, media)

        except:
            pass

    if msvcrt.kbhit():

        tecla = msvcrt.getch()

        if tecla == b' ':

            print("Aquisição finalizada")

            linha_vazia(ARQUIVO)

            break