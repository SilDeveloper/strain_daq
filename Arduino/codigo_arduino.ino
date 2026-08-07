// ============================================================
// HX711 — versão com mediana
// - mediana robusta (imune a outliers)
// - suavização exponencial
// - tara automática
// ============================================================

#define pino_SCK 5
#define pino_DT  4

#define NUMERO_DE_LEITURAS 40

long offset = 0;
float leituraFiltrada = 0;


// ------------------------------------------------------------
// Leitura bruta HX711
// ------------------------------------------------------------
long lerHX711() {
  long resultado = 0;

  while (digitalRead(pino_DT) == HIGH);

  for (int i = 0; i < 24; i++) {
    digitalWrite(pino_SCK, HIGH);
    resultado <<= 1;
    digitalWrite(pino_SCK, LOW);
    if (digitalRead(pino_DT)) resultado++;
  }

  digitalWrite(pino_SCK, HIGH);
  digitalWrite(pino_SCK, LOW);

  if (resultado & 0x800000) {
    resultado |= 0xFF000000;
  }

  return resultado;
}


// ------------------------------------------------------------
// Ordenação (bubble sort)
// Necessária para calcular a mediana
// ------------------------------------------------------------
void ordenar(long arr[], int n) {
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        long temp = arr[j];
        arr[j]   = arr[j + 1];
        arr[j + 1] = temp;
      }
    }
  }
}


// ------------------------------------------------------------
// Mediana
// Coleta NUMERO_DE_LEITURAS amostras, ordena e retorna
// o valor do meio — imune a picos elétricos
// ------------------------------------------------------------
long lerMediana() {
  long leituras[NUMERO_DE_LEITURAS];

  for (int i = 0; i < NUMERO_DE_LEITURAS; i++) {
    leituras[i] = lerHX711();
  }

  ordenar(leituras, NUMERO_DE_LEITURAS);

  // se número par de leituras, média dos dois do meio
  if (NUMERO_DE_LEITURAS % 2 == 0) {
    return (leituras[NUMERO_DE_LEITURAS / 2 - 1] +
            leituras[NUMERO_DE_LEITURAS / 2]) / 2;
  } else {
    return leituras[NUMERO_DE_LEITURAS / 2];
  }
}


// ------------------------------------------------------------
// Tara
// Coleta 5 medianas e usa a média delas como offset
// ------------------------------------------------------------
void tarar() {
  long soma = 0;
  for (int i = 0; i < 5; i++) {
    soma += lerMediana();
  }
  offset = soma / 5;
}


// ------------------------------------------------------------
// Setup
// ------------------------------------------------------------
void setup() {
  Serial.begin(9600);

  pinMode(pino_SCK, OUTPUT);
  pinMode(pino_DT, INPUT);
  digitalWrite(pino_SCK, LOW);

  delay(1000);

  tarar();

  leituraFiltrada = 0;
}


// ------------------------------------------------------------
// Loop
// ------------------------------------------------------------
void loop() {
  long leitura = lerMediana();

  // desconta o offset (tara)
  leitura -= offset;

  // suavização exponencial
  // 0.85 = peso do histórico (estabilidade)
  // 0.15 = peso da leitura nova (velocidade de resposta)
  leituraFiltrada = 0.85 * leituraFiltrada + 0.15 * leitura;

  Serial.println((long)leituraFiltrada);

  delay(100);
}
