# Automação da Análise de Dados com n8n — MCCT DAQ

Workflow desenvolvido na plataforma **n8n** para automatizar etapas do processamento, da organização e da análise dos dados associados ao sistema de aquisição de dados (DAQ) desenvolvido no contexto de uma pesquisa acadêmica em Modelagem Computacional.

## 1. Contextualização

O sistema MCCT DAQ foi desenvolvido para aquisição e processamento de dados experimentais utilizando Arduino, módulo HX711, célula de carga e ferramentas computacionais em Python.

Como complemento ao sistema, este workflow explora a utilização da automação de processos para integrar etapas da análise dos dados, organizar informações extraídas de arquivos de entrada e auxiliar na elaboração de relatórios.

A automação busca tornar o fluxo de análise mais organizado e reproduzível, mantendo a interpretação dos resultados vinculada aos dados experimentais e aos procedimentos metodológicos adotados na pesquisa.

## 2. Objetivo

Automatizar parte do fluxo de análise dos dados experimentais, integrando as seguintes etapas:

- Recebimento dos arquivos de entrada por meio de um formulário do n8n;
- Extração e organização das informações presentes nos arquivos;
- Processamento dos dados e cálculo de estatísticas descritivas;
- Integração e comparação de resultados provenientes do sistema desenvolvido e do equipamento de referência;
- Encaminhamento das informações a um agente de inteligência artificial para auxiliar na elaboração de um relatório textual;
- Geração de um arquivo de saída com o conteúdo produzido.

## 3. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| n8n | Orquestração e automação do fluxo de processamento |
| Jupyter Notebook | Organização dos dados e dos procedimentos de análise |
| OpenRouter | Integração com um modelo de linguagem utilizado pelo agente de IA |
| Arduino e HX711 | Componentes do sistema de aquisição de dados |
| Python | Processamento e análise computacional dos dados |

## 4. Fluxo de processamento

De forma geral, o workflow segue as etapas abaixo:

1. **Entrada:** recebimento dos arquivos necessários à análise.
2. **Extração:** leitura e extração das informações dos arquivos.
3. **Processamento:** organização dos dados e cálculo de estatísticas descritivas.
4. **Comparação:** integração dos resultados e cálculo de diferenças entre as medições.
5. **Análise assistida por IA:** envio das informações processadas a um agente de inteligência artificial.
6. **Saída:** conversão do resultado em texto e gravação em arquivo.

O relatório gerado pela inteligência artificial deve ser tratado como material auxiliar de análise, e não como substituto da avaliação científica, da verificação dos cálculos ou da interpretação dos dados experimentais.

## 5. Estrutura dos arquivos

```text
n8n/
├── README.md
└── workflow.json
```

- `README.md`: documentação do workflow, dos requisitos e das instruções de execução.
- `workflow.json`: definição exportada do fluxo de automação, utilizada para importação no n8n.

## 6. Requisitos e configuração

Para executar o workflow, são necessários:

- Uma instância do n8n em funcionamento;
- Os arquivos de entrada no formato esperado pelo fluxo;
- Uma credencial própria e válida para o serviço de modelo de linguagem configurado;
- Os caminhos de entrada e saída devidamente configurados no ambiente de execução.

### Como importar o workflow

1. Abra sua instância do n8n.
2. Utilize a opção de importação de workflow a partir de arquivo ou do conteúdo JSON.
3. Selecione `workflow.json`.
4. Configure a credencial do OpenRouter no ambiente do n8n.
5. Verifique os caminhos utilizados para leitura e gravação de arquivos.
6. Confira os campos esperados pelo formulário e os formatos dos arquivos de entrada.
7. Execute um teste com arquivos de exemplo antes de utilizar dados experimentais.

**Observação:** os caminhos de arquivos e as credenciais podem depender da configuração local do n8n. A importação do JSON, isoladamente, não garante que todas as dependências estejam configuradas.

## 7. Reprodutibilidade e segurança

Para favorecer a reprodutibilidade, recomenda-se manter a definição do workflow versionada e documentar eventuais alterações nos nós, nas fórmulas e nos parâmetros utilizados.

Antes de publicar ou compartilhar o projeto:

- Não inclua chaves de API, tokens, senhas ou credenciais no arquivo exportado.
- Não publique dados experimentais confidenciais ou arquivos locais desnecessários.
- Verifique os caminhos de arquivos e as configurações específicas do ambiente.
- Confirme os resultados dos cálculos independentemente do texto produzido pelo modelo de linguagem.

O workflow disponibilizado neste repositório deve ser entendido como uma ferramenta de automação complementar ao sistema DAQ, sujeita à verificação de suas configurações e dos resultados produzidos.

## 8. Relação com o projeto principal

Este workflow integra o repositório [strain_daq](https://github.com/SilDeveloper/strain_daq), dedicado ao desenvolvimento do sistema de aquisição de dados e de suas ferramentas computacionais.

Para conhecer o sistema completo, sua arquitetura e os demais componentes de software, consulte o README principal do repositório.