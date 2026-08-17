# Sistema de Análise de Atendimentos de Suporte Técnico

FIC_DEV — Módulo Python para IA — Desafio 1

Equipe: Felipe Ferreira Aguiar · Líbia Canhete Alves e Cruz · Victor Griggi Moreira Regis da Silva
Turma: Noturno

## Descrição

Aplicação de linha de comando que lê os registros de atendimento vindos de CSV, JSON e TXT, valida cada registro, padroniza os dados, calcula indicadores e exporta o resultado em CSV, JSON e gráficos PNG.

Os módulos em `src/` são separados por responsabilidade: `leitura.py` (config e arquivos de entrada), `validacao.py` (regras de aceitação), `processamento.py` (Pandas/NumPy), `relatorios.py` (Matplotlib e exportação) e `main.py` (orquestra tudo e configura o log).

Uma linha inválida não interrompe a execução: é recusada, o motivo vai para `output/erros.log` e o programa segue.

## Ambiente virtual

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python -m src.main
```

Testes:

```bash
pytest
```

## Arquivos gerados

Tudo vai para `output/`:

- `atendimentos_processados.csv` — os registros já limpos e sem duplicidade
- `resumo.json` — os indicadores
- `erros.log` — o motivo de cada recusa
- `graficos/` — os PNGs

## Números da última execução

Das 150 linhas do CSV, 143 passaram na validação e 7 foram recusadas. Depois de remover o protocolo duplicado sobraram 142 atendimentos.

## Decisões para tratar dados inválidos

São obrigatórios `protocolo`, `data`, `email`, `status` e `tempo_minutos`. `categoria` e `descricao` são opcionais.

Recusamos o registro quando o dado não tem conserto:

- campo obrigatório vazio
- e-mail sem domínio ou sem TLD, como `email-invalido` e `nome@dominio`
- data que não existe no calendário, como `31/02/2026`
- tempo não numérico (`muito`) ou menor que 1 minuto (`-15`)

O resto a gente aproveita e registra advertência no log:

- as datas vêm em 4 formatos diferentes e todas viram `AAAA-MM-DD`
- protocolo fora do padrão, como `PROTOCOLO-80`: o atendimento existiu, o
  errado é só a formatação, então descartar perderia um dado real
- tempo muito alto, como os 2000 minutos: atendimento demorado ainda é
  atendimento, e ele aparece como outlier na normalização
- categoria que não bate com nenhum sinônimo do `categorias.json` vira
  `Não classificada`
- protocolo repetido: fica só a primeira ocorrência

Manter esse registro de 2000 minutos tem duas consequências visíveis, e as duas
são propositais:

Na normalização, que é min-max sobre `tempo_minutos`, ele empurra todos os
outros para o começo da escala.

No gráfico de tempo médio, ele cai em `Instalação de programas` e sozinho leva a
média da categoria de 86 para 260 minutos, em 11 atendimentos resolvidos. A
barra dá a impressão de que instalação é disparado o pior atendimento, e não é.
Mantivemos a média porque é o indicador que o enunciado pede, e o boxplot ao
lado existe justamente para mostrar o ponto isolado que a média esconde. Os dois
gráficos precisam ser lidos juntos.

## Uso de ferramentas de IA

> A preencher antes da entrega, com o que cada um usou.

**Ferramenta:**

**Para quê:**

**Exemplos de prompt:**

**O que a gente revisou ou mudou depois:**

## Requisitos Funcionais

[✓] - Inicialização
  > O sistema deverá ser executado pelo comando: python -m src.main

[✓] - Leitura dos dados
  > O sistema deverá ler os arquivos CSV, JSON e TXT indicados no arquivo de configuração.

[✓] - Validação
  > Cada registro deverá ser classificado como válido ou inválido. A aplicação deverá apresentar o motivo da rejeição de registros inválidos.

[✓] - Tratamento dos dados
  > O sistema deverá:

    - [✓] remover espaços desnecessários;
    - [✓] uniformizar maiúsculas e minúsculas;
    - [✓] padronizar categorias;
    - [✓] converter datas;
    - [✓] tratar valores ausentes;
    - [✓] eliminar duplicidades pelo protocolo.

[✓] - Análise
  > O sistema deverá produzir indicadores estatísticos utilizando Pandas e NumPy.

[✓] - Visualização
  > O sistema deverá gerar e salvar pelo menos dois gráficos em formato PNG.

[✓] - Exportação
  > O sistema deverá gerar:

  - [✓] um CSV com os dados tratados;
  - [✓] um JSON com o resumo dos indicadores;
  - [✓] um arquivo de log com os problemas encontrados.

[✓] - Tolerância a falhas
  > A ocorrência de uma linha inválida não poderá encerrar toda a aplicação.
