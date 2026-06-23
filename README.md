# Sistema de Pesagem e Aquisição de Dados de Baixo Custo com Arduino

Sistema de aquisição de dados (DAQ) de baixo custo desenvolvido como parte de dissertação de mestrado no Programa de Pós-Graduação em Modelagem Computacional em Ciência e Tecnologia da Universidade Federal Fluminense (UFF).

O sistema integra uma célula de carga do tipo Single Point, o módulo HX711 e o microcontrolador Arduino Uno para medição de força e estimativa de massa, com processamento e calibração realizados em Python.

---

## Visão Geral

O sistema realiza:

- Aquisição dos sinais da célula de carga;
- Amplificação e conversão analógico-digital através do HX711;
- Transmissão dos dados pelo Arduino;
- Processamento e calibração em Python;
- Conversão automática das leituras RAW em massa (g).

Fluxo do sistema:

Célula de Carga → HX711 → Arduino → Computador → Python

---

## Hardware Utilizado

- Arduino Uno
- Célula de carga Single Point 1kg
- Módulo HX711
- Prato circular em MDF (150 mm de diâmetro)
- Cabos de conexão
- Estrutura mecânica de suporte
- Computador para aquisição e processamento

---

## Software Utilizado

- Arduino IDE
- Python 3.x
- PySerial
- NumPy
- Matplotlib

---

## Estrutura do Repositório

```
strain_daq/
│
├── arduino/
│   └── codigo_arduino.ino
│
├── python/
│   ├── calibracao.py
│   ├── reprocessar_calibracao.py
│   ├── validacao.py
│   └── main.py
│
├── data/
│
└── README.md
```

---

## Descrição dos arquivos

**`codigo_arduino.ino`**
Firmware embarcado no Arduino Uno. A cada ciclo, coleta 40 leituras brutas do HX711, calcula a mediana por ordenação (bubble sort) e aplica suavização exponencial. Na inicialização, realiza tara automática calculando a média de 5 medianas consecutivas sem carga. O valor final é transmitido via porta serial 9600.

**`calibracao.py`**
Coleta 15 leituras consecutivas para cada massa de referência, com intervalo de estabilização de 5 segundos antes de cada ponto. Cada leitura individual é gravada imediatamente em um CSV bruto na pasta `data/`. Ao final, gera também um CSV resumo com média, desvio padrão e resíduos da regressão linear, além do gráfico da curva de calibração com barras de erro.

**`reprocessar_calibracao.py`**
Lê o CSV bruto gerado pela calibração e seleciona apenas as 5 últimas leituras de cada ponto, correspondentes à região de maior estabilidade após o assentamento da carga. Recalcula os parâmetros da regressão linear e gera nova curva de calibração. Não requer o Arduino conectado.

**`validacao.py`**
Realiza 3 repetições independentes para cada massa de referência, com espera de 20 segundos por repetição. Calcula e exibe média, desvio padrão, erro absoluto e erro relativo. Salva os resultados em CSV na pasta `data/`.

**`main.py`**
Leitura contínua em tempo real. Monitora um histórico de 12 leituras consecutivas e detecta automaticamente quando o peso estabilizou (variação menor que 0,5 g), exibindo o valor confirmado no terminal.

---
## Trabalho Acadêmico

Este projeto foi desenvolvido como parte da dissertação de mestrado apresentada ao Programa de Pós-Graduação em Modelagem Computacional em Ciência e Tecnologia da Universidade Federal Fluminense (UFF).

Título:

**Desenvolvimento e Validação de um Sistema de Pesagem e Aquisição de Dados de Baixo Custo Utilizando Arduino**

---

## Licença

Este projeto é disponibilizado exclusivamente para fins acadêmicos, educacionais e de pesquisa.
