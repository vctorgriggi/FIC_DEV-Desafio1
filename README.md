# Sistema de Análise de Atendimentos de Suporte Técnico

FIC_DEV — Módulo Python para IA — Desafio 1

Equipe: Felipe · Libia · Victor Griggi Moreira Regis da Silva
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

Saídas em `output/`. Para rodar os testes: `python -m pytest`.

## Decisões para tratar dados inválidos

São obrigatórios `protocolo`, `data`, `email`, `categoria`, `status` e `tempo_minutos`; `descricao` é opcional. Recusamos o registro quando o dado não tem conserto:

- campo obrigatório vazio;
- e-mail sem domínio ou sem TLD (`email-invalido`, `nome@dominio`);
- data que não existe no calendário (`31/02/2026`);
- tempo não numérico (`muito`) ou menor que 1 minuto (`-15`).

O que dá pra aproveitar, aproveitamos, registrando advertência no log:

- **data em 4 formatos diferentes** — convertida para `AAAA-MM-DD`;
- **protocolo fora do padrão** (`PROTOCOLO-80`) — o atendimento aconteceu, o
  que está errado é a formatação; descartar perderia um dado real;
- **tempo muito alto** (`2000`) — atendimento demorado ainda é atendimento, e
  ele importa justamente na normalização com NumPy;
- **categoria sem correspondência** no `categorias.json` — entra como
  `Não classificada`;
- **protocolo repetido** (`SUP-2026-0001`) — fica só a primeira ocorrência.

## Uso de ferramentas de IA

> Definir

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

[ ] - Análise
  > O sistema deverá produzir indicadores estatísticos utilizando Pandas e NumPy.

[✓] - Visualização
  > O sistema deverá gerar e salvar pelo menos dois gráficos em formato PNG.

[] - Exportação
  > O sistema deverá gerar:
  
  - [] um CSV com os dados tratados;
  - [] um JSON com o resumo dos indicadores;
  - [] um arquivo de log com os problemas encontrados.

[] - Tolerância a falhas
  > A ocorrência de uma linha inválida não poderá encerrar toda a aplicação.