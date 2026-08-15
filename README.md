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
