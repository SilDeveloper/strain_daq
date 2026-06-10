# Sistema de Pesagem e Aquisição de Dados de Baixo Custo com Arduino

Sistema de pesagem desenvolvido utilizando célula de carga Single Point, módulo HX711, Arduino Uno e processamento em Python.

O projeto foi desenvolvido como parte do Trabalho de Conclusão de Curso, com o objetivo de avaliar a viabilidade de soluções de baixo custo para aplicações de pesagem, instrumentação e aquisição de dados.

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
- Célula de carga Single Point
- Módulo HX711
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
│   ├── aquisicao.py
│   └── balanca.py
│
├── imagens/
│
├── dados/
│
└── README.md
```

---

## Calibração

A calibração foi realizada utilizando massas de referência entre 0 g e 38 g.

O ajuste linear apresentou:

- R² = 0,978

permitindo a conversão dos valores RAW fornecidos pelo HX711 em valores de massa.

---

## Resultados

Durante os testes experimentais:

- O sistema apresentou comportamento aproximadamente linear;
- Foi possível estimar massas utilizando regressão linear;
- Um ensaio de validação com massa de 10 g resultou em leitura aproximada de 10,7 g;
- O sistema demonstrou viabilidade para aplicações didáticas e experimentais.

---

## Trabalho Acadêmico

Este projeto foi desenvolvido como Trabalho de Conclusão de Curso.

Título:

**Desenvolvimento e Validação de um Sistema de Pesagem e Aquisição de Dados de Baixo Custo Utilizando Arduino**

---

## Licença

Este projeto é disponibilizado para fins acadêmicos e educacionais.
