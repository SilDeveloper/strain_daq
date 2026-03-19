![Python](https://img.shields.io/badge/Python-3.x-blue)

# 📡 Sistema de Aquisição de Dados Extensométricos (DAQ) de Baixo Custo

Este projeto tem como objetivo o desenvolvimento de um sistema de aquisição de dados extensométricos utilizando componentes de baixo custo, como Arduino e o módulo HX711, aplicado a medições de deformação mecânica.

---

## 📌 Descrição

O sistema realiza a leitura de um extensômetro (strain gauge) configurado em 1/4 de ponte de Wheatstone, utilizando o conversor HX711 para amplificação e digitalização do sinal.

Os dados são enviados via comunicação serial para um sistema em Python responsável pelo processamento, filtragem e armazenamento.

---

## 🧩 Componentes Utilizados

* Arduino
* Módulo HX711
* Extensômetro (strain gauge ~120Ω)
* Resistores (~115Ω)
* Protoboard (fase atual)
* Cabos jumper

---

## ⚙️ Arquitetura do Sistema

### 🔹 Hardware

* Ponte de Wheatstone (1/4 de ponte)
* HX711 (ADC de alta precisão)
* Arduino (leitura e transmissão)

### 🔹 Software

* Python (VS Code)
* Leitura serial em tempo real
* Filtragem de dados
* Registro em CSV
* Estrutura modular

---

## 📁 Estrutura do Projeto

```bash
strain_daq/
│
├── main.py
├── serial_reader.py
├── csv_logger.py
├── filters.py
├── calibration.py
├── plotter.py
└── data/  # arquivos CSV (ignorados no Git)
```

---

## 📊 Funcionalidades

* Leitura contínua via serial
* Filtragem de ruído (média móvel)
* Remoção de valores aberrantes
* Registro de dados com timestamp
* Preparação para calibração e análise

---

## ⚠️ Estado Atual

O sistema encontra-se funcional, porém apresenta:

* Ruído nas medições
* Sensibilidade a interferências externas
* Instabilidade devido à montagem em protoboard

Melhorias estão sendo implementadas no processamento e na montagem física.

---

## 🎯 Próximos Passos

* Refinamento da filtragem de sinais
* Calibração experimental com cargas conhecidas
* Conversão de RAW → força → deformação
* Geração de gráficos automáticos
* Integração com interface web (Flask)

---

## 📌 Observações

Este projeto faz parte de uma pesquisa de mestrado em **Modelagem Computacional**, com foco em instrumentação de baixo custo.

---

## 📄 Licença

Uso acadêmico.
