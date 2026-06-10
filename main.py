import serial
import serial.tools.list_ports
import time
from collections import deque

# ============================================================
# BALANÇA INTELIGENTE DAQ — COM STATUS DE ESTABILIZAÇÃO
# Célula de carga GI + HX711 + Arduino
# ============================================================

# Valores gerados na sua calibração de sucesso:
FATOR_CALIBRACAO = 143728.863800
DESLOCAMENTO = 1769.262400

# Parâmetros de estabilidade
TOLERANCIA_GRAMAS = 0.5     # O peso pode oscilar no máximo 0.5g para ser considerado estável
AMOSTRAS_ESTABILIDADE = 12  # Quantas leituras seguidas avaliamos

historico_pesos = deque(maxlen=AMOSTRAS_ESTABILIDADE)
ultimo_peso_confirmado = 0.0
esta_calculando = False

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

print("Aguardando inicialização...", end='', flush=True)
time.sleep(2)
arduino.flushInput()
print(" pronto!\n")

def calcular_massa(leitura_bruta):
    forca = (leitura_bruta - DESLOCAMENTO) / FATOR_CALIBRACAO
    massa_gramas = (forca / 9.81) * 1000
    return massa_gramas

print("=" * 50)
print("             BALANÇA DIGITAL ATIVA             ")
print("        Coloque o objeto no prato para ler     ")
print("=" * 50 + "\n")

print(f"[  ] Balança vazia (0.0 g)", flush=True)

try:
    while True:
        linha = arduino.readline().decode('utf-8').strip()
        try:
            leitura_atual = float(linha)
            peso_atual = calcular_massa(leitura_atual)
            
            if abs(peso_atual) < 0.5:
                peso_atual = 0.0
                
            historico_pesos.append(peso_atual)
            
            if len(historico_pesos) == AMOSTRAS_ESTABILIDADE:
                menor_peso = min(historico_pesos)
                maior_peso = max(historico_pesos)
                variacao = maior_peso - menor_peso
                peso_medio = sum(historico_pesos) / AMOSTRAS_ESTABILIDADE
                
                # SE O PESO MUDOU e a balança está oscilando (variação alta)
                if abs(peso_medio - ultimo_peso_confirmado) >= 1.0 and variacao > TOLERANCIA_GRAMAS:
                    if not esta_calculando:
                        print(f"\r[ ⏳ ] Peso identificado. Calculando...", end='', flush=True)
                        esta_calculando = True
                
                # SE ESTABILIZOU (variação menor ou igual à tolerância)
                elif variacao <= TOLERANCIA_GRAMAS:
                    peso_final = round(peso_medio, 1)
                    
                    # Se o peso estabilizou em um valor novo diferente do anterior
                    if abs(peso_final - ultimo_peso_confirmado) >= 0.5:
                        # Se saiu do estado "Calculando", pula uma linha para registrar o peso final
                        if esta_calculando:
                            print("") 
                        
                        if peso_final == 0.0:
                            print(f"[  ] Prato livre — Balança zerada (0.0 g)", flush=True)
                        else:
                            print(f"[  ] Peso em gramas: {peso_final:.1f} g", flush=True)
                            
                        ultimo_peso_confirmado = peso_final
                        esta_calculando = False
            
        except ValueError:
            continue
            
        time.sleep(0.04)

except KeyboardInterrupt:
    print("\n\nPrograma finalizado pelo usuário.")
    arduino.close()
