import logging
import sys
from pathlib import Path

from src import leitura, processamento, relatorios
from src.leitura import ArquivoAusenteError
from src.validacao import RegistroInvalidoError, protocolo_valido, validar_registro

"""
    Descrição do problema:
    
    A coordenação do curso FIC_DEV recebe solicitações de suporte relacionadas a acesso ao ambiente virtual, instalação de programas, configuração do Python, problemas com senhas e dificuldades na execução das atividades.
    Os atendimentos são registrados em arquivos provenientes de diferentes fontes. Entretanto, os dados apresentam problemas como:
        - campos vazios;
        - categorias escritas de maneiras diferentes;
        - datas em formatos distintos;
        - tempos de atendimento inválidos;
        - e-mails incorretos;
        - registros duplicados;
        - dados armazenados em CSV, JSON e TXT.
"""


RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_CONFIG = RAIZ / "data" / "config.json"


# Infraestrutura
def preparar_diretorios(saida: Path) -> None:
    # Preparação dos diretórios de saída, criando a pasta de saída e a pasta de gráficos se não existirem.
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "graficos").mkdir(exist_ok=True)


def configurar_logger(caminho_log: Path) -> logging.Logger:
    """Configura o logger: console em INFO e arquivo em WARNING."""
    logger = logging.getLogger("suporte")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    arquivo = logging.FileHandler(caminho_log, mode="w", encoding="utf-8")
    arquivo.setLevel(logging.WARNING)
    arquivo.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(arquivo)
    return logger


# Etapa de validação
def validar_todos(registros: list[dict]) -> tuple[list[dict], list[dict]]:
    """Valida a lista inteira sem deixar uma linha ruim derrubar a execução.

    Returns:
        Tupla (válidos, rejeitados). Cada rejeitado traz linha, protocolo
        e o motivo da recusa.
    """
    logger = logging.getLogger("suporte.validacao")
    validos: list[dict] = []
    rejeitados: list[dict] = []

    # start=2 porque a linha 1 do arquivo é o cabeçalho
    for linha, registro in enumerate(registros, start=2):
        try:
            atendimento = validar_registro(registro)

        except RegistroInvalidoError as e:
            protocolo = (registro.get("protocolo") or "?").strip()
            logger.warning("Linha %d (%s) rejeitada: %s", linha, protocolo, e)
            rejeitados.append(
                {"linha": linha, "protocolo": protocolo, "motivo": str(e)}
            )

        except Exception:
            logger.exception("Linha %d: erro inesperado na validação", linha)
            rejeitados.append(
                {
                    "linha": linha,
                    "protocolo": (registro.get("protocolo") or "?").strip(),
                    "motivo": "erro inesperado, ver erros.log",
                }
            )

        else:
            # Protocolo fora do padrão não descarta o atendimento, só avisa
            if not protocolo_valido(atendimento["protocolo"]):
                logger.warning(
                    "Linha %d: protocolo '%s' fora do padrão SUP-AAAA-NNNN",
                    linha,
                    atendimento["protocolo"],
                )
            validos.append(atendimento)

    return validos, rejeitados


# Saída no terminal
def exibir_resumo_validacao(validos: list[dict], rejeitados: list[dict]) -> None:
    total = len(validos) + len(rejeitados)
    sep = "=" * 70

    print(f"\n{sep}")
    print(" LEITURA E VALIDAÇÃO DOS ATENDIMENTOS")
    print(sep)
    print(f" Linhas lidas         : {total}")
    print(f" Registros válidos    : {len(validos)} ({len(validos) / total:.1%})")
    print(f" Registros rejeitados : {len(rejeitados)} ({len(rejeitados) / total:.1%})")

    if rejeitados:
        print(f"\n {'LINHA':>5}  {'PROTOCOLO':<15} MOTIVO")
        print(f" {'-' * 5}  {'-' * 15} {'-' * 44}")
        for r in rejeitados:
            print(f" {r['linha']:>5}  {r['protocolo']:<15} {r['motivo']}")

    print(f"{sep}\n")


def exibir_resumo_tratamento(antes: int, df_tratado) -> None:
    sep = "=" * 70
    depois = len(df_tratado)
    nao_classificados = int(
        (df_tratado["categoria"] == processamento.CATEGORIA_PADRAO).sum()
    )

    print(sep)
    print(" TRATAMENTO DOS DADOS")
    print(sep)
    print(f" Válidos antes do tratamento : {antes}")
    print(f" Duplicidades removidas      : {antes - depois}")
    print(f" Registros após tratamento   : {depois}")
    print(f" Categoria não classificada  : {nao_classificados}")
    print(f"{sep}\n")


def exibir_observacoes(protocolos: list[str], telefones: list[str]) -> None:
    sep = "=" * 70

    print(sep)
    print(" DADOS EXTRAÍDOS DAS OBSERVAÇÕES (regex)")
    print(sep)
    print(f" Protocolos citados : {', '.join(protocolos) or 'nenhum'}")
    print(f" Telefones de retorno: {', '.join(telefones) or 'nenhum'}")
    print(f"{sep}\n")


# Pipeline
def main() -> None:
    try:
        # Carrega a configuração do arquivo de configuração.
        config = leitura.carregar_config(CAMINHO_CONFIG)
        caminhos = leitura.resolver_caminhos(config, RAIZ)
        leitura.verificar_entradas(caminhos)
    except ArquivoAusenteError as e:
        # O logger ainda não existe: sem config não se sabe onde gravar o log.
        print(f"Erro de configuração: {e}", file=sys.stderr)
        sys.exit(1)

    # Prepara os diretórios de saída.
    preparar_diretorios(caminhos["saida"])

    # Configura o logger.
    logger = configurar_logger(caminhos["saida"] / "erros.log")
    logger.info("=== Início da execução ===")

    try:
        categorias = leitura.carregar_categorias(caminhos["categorias"])
        brutos = leitura.ler_atendimentos(
            caminhos["atendimentos"], config["separador_csv"]
        )

    except ArquivoAusenteError as e:
        logger.error("Falha na leitura dos dados: %s", e)
        sys.exit(1)

    logger.info("%d categorias oficiais carregadas", len(categorias))
    logger.info("%d linhas lidas do CSV", len(brutos))

    validos, rejeitados = validar_todos(brutos)
    logger.info("%d válidos, %d rejeitados", len(validos), len(rejeitados))
    exibir_resumo_validacao(validos, rejeitados)

    df_tratado = processamento.tratar_dados(validos, categorias)
    exibir_resumo_tratamento(len(validos), df_tratado)

    graficos = relatorios.gerar_graficos(df_tratado, caminhos["saida"] / "graficos")
    print(f"{len(graficos)} gráfico(s) salvo(s) em: {caminhos['saida'] / 'graficos'}\n")

    texto = leitura.ler_observacoes(caminhos["observacoes"])
    protocolos = leitura.extrair_protocolos(texto)
    telefones = leitura.extrair_telefones(texto)

    # Registra o número de protocolos e telefones extraídos.
    logger.info(
        "Observações: %d protocolos e %d telefones extraídos",
        len(protocolos),
        len(telefones),
    )

    exibir_observacoes(protocolos, telefones)

    estatisticas = processamento.calcular_estatisticas(
        df_tratado, len(rejeitados), len(brutos)
    )
    
    relatorios.gerar_json(estatisticas, caminhos["saida"] / "estatisticas.json")
    relatorios.gerar_csv(df_tratado, caminhos["saida"] / "atendimentos.csv")
    
    print(f"Log de advertências gravado em: {caminhos['saida'] / 'erros.log'}")
    logger.info("=== Fim da execução ===")


if __name__ == "__main__":
    main()
