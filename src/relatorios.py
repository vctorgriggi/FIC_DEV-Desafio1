"""FIC_DEV — Módulo Python para IA — Desafio 1

Equipe: Felipe Ferreira Aguiar · Líbia Canhete Alves e Cruz · Victor Griggi Moreira Regis da Silva
Turma: Noturno

Geração dos gráficos com Matplotlib e exportação do CSV e do JSON.
"""

import csv
import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger("suporte.relatorios")

# Paleta: uma cor de destaque por gráfico (série única, sem necessidade de legenda)
COR_CATEGORIA = "#2a78d6"
COR_STATUS = "#eb6834"
COR_TEMPO = "#1baf7a"
COR_OUTLIER = "#d64545"

TINTA_PRIMARIA = "#0b0b0b"
TINTA_MUTED = "#898781"
LINHA_GRADE = "#e1e0d9"
LINHA_BASE = "#c3c2b7"


def _estilizar_eixo(ax, unidade: str = "", grade: str = "x") -> None:
    """Aplica o mesmo acabamento visual aos gráficos."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(LINHA_BASE)

    if grade == "y":
        ax.yaxis.grid(True, color=LINHA_GRADE, linewidth=0.8, zorder=0)
    else:
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


def grafico_tempo_medio_por_categoria(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o gráfico de barras com o tempo médio (min) por categoria.

    Considera só o status resolvido: em atendimento aberto o tempo ainda
    está correndo, e entrar na média puxaria ela para baixo.
    """
    medias = (
        df.loc[df["status"] == "resolvido"]
        .groupby("categoria")["tempo_minutos"]
        .apply(lambda s: np.mean(s.to_numpy(dtype=float)))
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(medias.index, medias.values, color=COR_TEMPO, height=0.65, zorder=3)
    ax.set_xlim(0, medias.values.max() * 1.15)
    _estilizar_eixo(ax)
    _rotular_barras(ax, medias.values, sufixo=" min")

    ax.set_title(
        "Tempo médio por categoria, só dos atendimentos resolvidos",
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


def grafico_boxplot_tempo_por_categoria(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o boxplot do tempo de atendimento (min) por categoria.

    Cada caixa mostra mediana, quartis e valores atípicos (pontos vermelhos),
    para a média sozinha não esconder a variação nem os outliers.
    """
    ordem = (
        df.groupby("categoria")["tempo_minutos"]
        .median()
        .sort_values(ascending=True)
        .index
    )
    grupos = [
        df.loc[df["categoria"] == categoria, "tempo_minutos"].to_numpy(dtype=float)
        for categoria in ordem
    ]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.boxplot(
        grupos,
        tick_labels=ordem,
        vert=False,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": COR_TEMPO, "edgecolor": COR_TEMPO, "linewidth": 1.2},
        medianprops={"color": TINTA_PRIMARIA, "linewidth": 1.6},
        whiskerprops={"color": TINTA_MUTED, "linewidth": 1.2},
        capprops={"color": TINTA_MUTED, "linewidth": 1.2},
        flierprops={
            "marker": "o",
            "markersize": 5,
            "markerfacecolor": COR_OUTLIER,
            "markeredgecolor": "none",
            "alpha": 0.85,
        },
    )

    _estilizar_eixo(ax)
    ax.set_title(
        "Distribuição do tempo de atendimento por categoria",
        fontsize=13,
        color=TINTA_PRIMARIA,
        pad=14,
    )
    ax.set_xlabel("Minutos", fontsize=10, color=TINTA_MUTED)

    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor="white")
    plt.close(fig)

    logger.info("Gráfico salvo: %s", destino)
    return destino


def grafico_atendimentos_por_dia(df: pd.DataFrame, destino: Path) -> Path:
    """Gera o gráfico de linha com a quantidade de atendimentos por dia.

    Dias sem registro entram como zero, para a linha do tempo não pular datas.
    """
    diario = df.groupby("data").size().rename("quantidade").asfreq("D", fill_value=0)
    valores = diario.to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(diario.index, valores, color=COR_CATEGORIA, alpha=0.12, zorder=2)
    ax.plot(
        diario.index,
        valores,
        color=COR_CATEGORIA,
        linewidth=2,
        marker="o",
        markersize=4.5,
        markerfacecolor="white",
        markeredgecolor=COR_CATEGORIA,
        markeredgewidth=1.4,
        zorder=3,
    )

    _estilizar_eixo(ax, grade="y")
    ax.set_ylim(0, valores.max() * 1.15)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

    ax.set_title("Atendimentos por dia", fontsize=13, color=TINTA_PRIMARIA, pad=14)
    ax.set_xlabel("Data", fontsize=10, color=TINTA_MUTED)
    ax.set_ylabel("Quantidade de atendimentos", fontsize=10, color=TINTA_MUTED)

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
        grafico_tempo_medio_por_categoria(
            df, diretorio / "tempo_medio_por_categoria.png"
        ),
        grafico_boxplot_tempo_por_categoria(
            df, diretorio / "boxplot_tempo_por_categoria.png"
        ),
        grafico_atendimentos_por_dia(df, diretorio / "atendimentos_por_dia.png"),
    ]

    logger.info("%d gráfico(s) gerado(s) em %s", len(caminhos), diretorio)
    return caminhos


def gerar_json(data: dict, destino: Path) -> Path:
    """Gera um arquivo JSON com os dados."""

    with open(destino, "w", encoding="utf-8") as arquivo:
        json.dump(data, arquivo, indent=4, ensure_ascii=False)

    logger.info("Arquivo JSON salvo: %s", destino)
    return destino


def gerar_csv(data: dict | pd.DataFrame, destino: Path) -> Path:
    """Gera um arquivo CSV com os dados."""

    if isinstance(data, pd.DataFrame):
        data.to_csv(
            destino,
            sep=";",
            index=False,
            encoding="utf-8",
            date_format="%Y-%m-%d",
        )
    else:
        with open(destino, "w", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=data.keys())
            writer.writeheader()
            writer.writerows(data)

    logger.info("Arquivo CSV salvo: %s", destino)
    return destino
