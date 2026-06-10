import serial
import serial.tools.list_ports
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time

# ============================================================
# CALIBRAÇÃO — Sistema DAQ
# Célula de carga GI + HX711 + Arduino
#
# IMPORTANTE: esse código assume que o Arduino já fez a tara
# automaticamente no boot. Os valores que chegam já estão
# com o zero descontado — próximos de 0 sem carga.
# ============================================================


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

# aguarda o Arduino inicializar e fazer a tara
print("Aguardando Arduino inicializar e tarar...", end='', flush=True)
time.sleep(3)
arduino.flushInput()
print(" pronto!\n")


# ------------------------------------------------------------
# PASSO 2 — Função para coletar leituras estáveis
# ------------------------------------------------------------

def coletar_leitura(amostras=15):
    """
    Coleta várias leituras e retorna a média.
    O Arduino já envia valores filtrados e zerados.
    """
    valores = []
    tentativas = 0

    while len(valores) < amostras and tentativas < amostras * 3:
        linha = arduino.readline().decode('utf-8').strip()
        tentativas += 1
        try:
            v = float(linha)
            valores.append(v)
        except ValueError:
            continue

    if not valores:
        return None

    return np.mean(valores)


# ------------------------------------------------------------
# PASSO 3 — Sequência de calibração
# ------------------------------------------------------------
# Pesos disponíveis: 1g, 2g, 5g, 10g, 20g
# Combinações sugeridas:

pesos_gramas = [0, 1, 2, 3, 5, 6, 7, 8, 10, 15, 20, 38]
# 0g   → nenhum peso (confirma que tara está ok)
# 1g   → pesinho 1g
# 2g   → pesinho 2g
# 3g   → 1g + 2g
# 5g   → pesinho 5g
# 6g   → 5g + 1g
# 7g   → 5g + 2g
# 8g   → 5g + 2g + 1g
# 10g  → pesinho 10g
# 15g  → 10g + 5g
# 20g  → pesinho 20g
# 38g  → todos juntos

leituras_coletadas = []

print("=" * 50)
print("INÍCIO DA CALIBRAÇÃO")
print("=" * 50)
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

    leitura = coletar_leitura(amostras=15)

    if leitura is None:
        print("  ERRO: não foi possível ler o Arduino. Pulando esse ponto.")
        continue

    leituras_coletadas.append((peso, leitura))
    print(f"  → {peso}g = leitura {leitura:.1f}")

print("\n" + "=" * 50)
print("Coleta finalizada!")
print("=" * 50)


# ------------------------------------------------------------
# PASSO 4 — Converter massa para força
# ------------------------------------------------------------

massas   = np.array([p for p, _ in leituras_coletadas])
leituras = np.array([l for _, l in leituras_coletadas])

# Força em Newtons: F = (massa em kg) × 9,81
forcas = (massas / 1000) * 9.81


# ------------------------------------------------------------
# PASSO 5 — Regressão linear
# ------------------------------------------------------------
# Como o Arduino já fez a tara, o intercept deve ser ~0
# A relação é: leitura = inclinacao × força

inclinacao, deslocamento, correlacao, _, incerteza = stats.linregress(
    forcas,    # eixo X — força real em Newtons
    leituras   # eixo Y — leitura do Arduino (já zerada)
)

qualidade = correlacao ** 2


# ------------------------------------------------------------
# PASSO 6 — Resultados
# ------------------------------------------------------------

print("\n===== RESULTADO DA CALIBRAÇÃO =====")
print(f"Fator de calibração: {inclinacao:.4f} unidades por Newton")
print(f"Deslocamento (deve ser ≈ 0): {deslocamento:.4f}")
print(f"Qualidade R²: {qualidade:.6f}")
print(f"Incerteza do fator: {incerteza:.6f}")

if qualidade > 0.999:
    print("\n✅ Calibração excelente — R² acima de 0,999")
elif qualidade > 0.99:
    print("\n⚠️  Calibração aceitável — R² entre 0,99 e 0,999")
else:
    print("\n❌ Calibração ruim — verifique a montagem e os pesos")

# salva os coeficientes para usar no main.py
print(f"\n# Cole isso no seu main.py:")
print(f"FATOR_CALIBRACAO = {inclinacao:.6f}")
print(f"DESLOCAMENTO     = {deslocamento:.6f}")


# ------------------------------------------------------------
# PASSO 7 — Funções de conversão
# ------------------------------------------------------------

def leitura_para_forca(leitura):
    """Converte leitura do Arduino em força (N)."""
    return (leitura - deslocamento) / inclinacao

def leitura_para_massa(leitura):
    """Converte leitura do Arduino em massa (g)."""
    return leitura_para_forca(leitura) / 9.81 * 1000


# ------------------------------------------------------------
# PASSO 8 — Gráfico
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5))

# pontos medidos
ax.scatter(forcas, leituras, color='#185FA5', zorder=5,
           s=60, label='Pontos de calibração')

# reta ajustada
x_fit = np.linspace(min(forcas), max(forcas), 100)
y_fit = inclinacao * x_fit + deslocamento
ax.plot(x_fit, y_fit, '--', color='#1D9E75', lw=2,
        label=f'Regressão linear (R² = {qualidade:.4f})')

# erro percentual por ponto
for f, l in zip(forcas, leituras):
    l_previsto = inclinacao * f + deslocamento
    if l_previsto != 0:
        erro = abs(l - l_previsto) / abs(l_previsto) * 100
        ax.annotate(f'{erro:.1f}%', (f, l),
                    textcoords='offset points', xytext=(5, 5),
                    fontsize=6.5, color='gray')

ax.set_xlabel('Força real (N)')
ax.set_ylabel('Leitura do Arduino (zerada)')
ax.set_title('Curva de Calibração — Célula de Carga GI + HX711')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('curva_calibracao.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nGráfico salvo como curva_calibracao.png")

arduino.close()
