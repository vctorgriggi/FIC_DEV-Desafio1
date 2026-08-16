import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger("suporte.relatorios")

# Paleta: uma cor de destaque por gráfico (série única, sem necessidade de legenda)
COR_CATEGORIA = "#2a78d6"
COR_STATUS = "#eb6834"
COR_TEMPO = "#1baf7a"

TINTA_PRIMARIA = "#0b0b0b"
TINTA_MUTED = "#898781"
LINHA_GRADE = "#e1e0d9"
LINHA_BASE = "#c3c2b7"


def _estilizar_eixo(ax, unidade: str = "") -> None:
    """Aplica o mesmo acabamento visual a todos os gráficos de barra."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(LINHA_BASE)

    ax.xaxis.grid(True, color=LINHA_GRADE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, colors=TINTA_MUTED, labelsize=10)
    ax.tick_params(axis="y", colors=TINTA_PRIMARIA)


def _rotular_barras(ax, valores, sufixo: str = "") -> None:
    limite = ax.get_xlim()[1]
    deslocamento = limite * 0.01
    for i, valor in enumerate(valores):
        ax.text(
            valor + deslocamento,
            i,
            f"{valor:.0f}{sufixo}",
            va="center",
            fontsize=10,
            color=TINTA_MUTED,
        )


def grafico_atendimentos_por_categoria(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o gráfico de barras com a quantidade de atendimentos por categoria."""
    contagem = df["categoria"].value_counts().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(contagem.index, contagem.values, color=COR_CATEGORIA, height=0.65, zorder=3)
    ax.set_xlim(0, contagem.values.max() * 1.15)
    _estilizar_eixo(ax)
    _rotular_barras(ax, contagem.values)

    ax.set_title(
        "Atendimentos por categoria", fontsize=13, color=TINTA_PRIMARIA, pad=14
    )
    ax.set_xlabel("Quantidade de atendimentos", fontsize=10, color=TINTA_MUTED)

    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor="white")
    plt.close(fig)

    logger.info("Gráfico salvo: %s", destino)
    return destino


def grafico_distribuicao_status(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o gráfico de barras com a quantidade de atendimentos por status."""
    contagem = df["status"].value_counts().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(contagem.index, contagem.values, color=COR_STATUS, height=0.55, zorder=3)
    ax.set_xlim(0, contagem.values.max() * 1.15)
    _estilizar_eixo(ax)
    _rotular_barras(ax, contagem.values)

    ax.set_title(
        "Distribuição dos atendimentos por status",
        fontsize=13,
        color=TINTA_PRIMARIA,
        pad=14,
    )
    ax.set_xlabel("Quantidade de atendimentos", fontsize=10, color=TINTA_MUTED)

    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor="white")
    plt.close(fig)

    logger.info("Gráfico salvo: %s", destino)
    return destino


def grafico_tempo_medio_por_categoria(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o gráfico de barras com o tempo médio (min) de atendimento por categoria."""
    medias = (
        df.groupby("categoria")["tempo_minutos"]
        .apply(lambda s: np.mean(s.to_numpy(dtype=float)))
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(medias.index, medias.values, color=COR_TEMPO, height=0.65, zorder=3)
    ax.set_xlim(0, medias.values.max() * 1.15)
    _estilizar_eixo(ax)
    _rotular_barras(ax, medias.values, sufixo=" min")

    ax.set_title(
        "Tempo médio de atendimento por categoria",
        fontsize=13,
        color=TINTA_PRIMARIA,
        pad=14,
    )
    ax.set_xlabel("Minutos (média)", fontsize=10, color=TINTA_MUTED)

    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor="white")
    plt.close(fig)

    logger.info("Gráfico salvo: %s", destino)
    return destino


def gerar_graficos(df: pd.DataFrame, diretorio: Path) -> list[Path]:
    """Gera e salva os gráficos PNG a partir do DataFrame já tratado.

    Returns:
        Lista com os caminhos dos arquivos PNG gerados.
    """
    diretorio.mkdir(parents=True, exist_ok=True)

    caminhos = [
        grafico_atendimentos_por_categoria(
            df, diretorio / "atendimentos_por_categoria.png"
        ),
        grafico_distribuicao_status(df, diretorio / "distribuicao_status.png"),
        grafico_tempo_medio_por_categoria(
            df, diretorio / "tempo_medio_por_categoria.png"
        ),
    ]

    logger.info("%d gráfico(s) gerado(s) em %s", len(caminhos), diretorio)
    return caminhos


def gerar_json(data: dict, destino: Path) -> Path:
    """Gera um arquivo JSON com os dados."""

    with open(destino, "w", encoding="utf-8") as arquivo:
        json.dump(data, arquivo, indent=4, ensure_ascii=False)

    logger.info("Arquivo JSON salvo: %s", destino)
    return destino
