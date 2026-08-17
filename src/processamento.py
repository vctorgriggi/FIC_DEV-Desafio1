import logging

import numpy as np
import pandas as pd

logger = logging.getLogger("suporte.processamento")

CATEGORIA_PADRAO = "Não classificada"

COLUNAS_TEXTO = ("protocolo", "email", "categoria", "status", "descricao")


def _mapa_sinonimos(categorias: dict) -> dict:
    """Inverte {oficial: [sinônimos]} em {sinônimo em minúsculo: oficial}."""
    mapa: dict[str, str] = {}

    for oficial, sinonimos in categorias.items():
        mapa[oficial.strip().lower()] = oficial
        for sinonimo in sinonimos:
            mapa[sinonimo.strip().lower()] = oficial
    return mapa


def padronizar_categoria(categoria: str, mapa: dict) -> str:
    """Traduz uma categoria livre para o nome oficial em categorias.json.

    Sem correspondência no mapa, cai em CATEGORIA_PADRAO ("Não classificada")
    em vez de descartar o atendimento.
    """
    return mapa.get(categoria.strip().lower(), CATEGORIA_PADRAO)


def normalizar_tempos(tempos: np.ndarray) -> np.ndarray:
    """Reescala os tempos para o intervalo [0, 1] pelo mínimo e máximo.

    Returns:
        Array normalizado, ou tudo zero se todos os tempos forem iguais.
    """
    minimo = tempos.min()
    amplitude = tempos.max() - minimo

    if amplitude == 0:
        return np.zeros_like(tempos)

    return (tempos - minimo) / amplitude


def tratar_dados(registros: list[dict], categorias: dict) -> pd.DataFrame:
    """Limpa e padroniza os atendimentos já validados.

    Aplica, nessa ordem: remoção de espaços, uniformização de
    caixa, padronização de categoria, preenchimento de
    descrição ausente, conversão da data para datetime e remoção de
    protocolos duplicados (mantendo a primeira ocorrência).

    Returns:
        DataFrame tratado, pronto para análise e geração de gráficos.
    """
    df = pd.DataFrame(registros)

    for coluna in COLUNAS_TEXTO:
        df[coluna] = df[coluna].astype(str).str.strip()

    df["protocolo"] = df["protocolo"].str.upper()
    df["email"] = df["email"].str.lower()
    df["status"] = df["status"].str.lower()

    df["descricao"] = df["descricao"].replace("", np.nan).fillna("Sem descrição")

    mapa = _mapa_sinonimos(categorias)
    df["categoria"] = df["categoria"].apply(lambda c: padronizar_categoria(c, mapa))
    nao_classificados = int((df["categoria"] == CATEGORIA_PADRAO).sum())
    if nao_classificados:
        logger.warning(
            "%d atendimento(s) com categoria sem correspondência -> '%s'",
            nao_classificados,
            CATEGORIA_PADRAO,
        )

    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")
    df["tempo_minutos"] = df["tempo_minutos"].astype(int)

    antes = len(df)
    df = df.drop_duplicates(subset="protocolo", keep="first").reset_index(drop=True)
    duplicados = antes - len(df)
    if duplicados:
        logger.warning(
            "%d protocolo(s) duplicado(s) removido(s), mantida a primeira ocorrência",
            duplicados,
        )

    df["tempo_normalizado"] = normalizar_tempos(
        df["tempo_minutos"].to_numpy(dtype=float)
    ).round(4)

    logger.info(
        "Tratamento concluído: %d atendimento(s) após limpeza e deduplicação", len(df)
    )
    return df


def calcular_estatisticas(df: pd.DataFrame, rejeitados: int, lidos: int) -> dict:
    """Calcula estatísticas sobre o DataFrame tratado.

    Returns:
        Dicionário com as estatísticas calculadas.
    """
    estatisticas = {
        "atendimentos_lidos": lidos,
        "atendimentos_rejeitados": rejeitados,
        "atendimentos_validos": len(df),
    }

    # Quantidade total de atendimentos;
    estatisticas["atendimentos_total"] = len(df)

    # Atendimentos por categoria;
    estatisticas["atendimentos_por_categoria"] = (
        df["categoria"].value_counts().to_dict()
    )

    # Atendimentos por status;
    estatisticas["atendimentos_por_status"] = df["status"].value_counts().to_dict()

    # Tempo médio de atendimento;
    estatisticas["tempo_medio_de_atendimento"] = df["tempo_minutos"].mean()

    # Mediana e desvio padrão do tempo, com NumPy;
    tempos = df["tempo_minutos"].to_numpy(dtype=float)
    estatisticas["tempo_mediano_de_atendimento"] = float(np.median(tempos))
    estatisticas["desvio_padrao_do_tempo"] = float(np.std(tempos))

    # Tempo médio de atendimento por categoria;
    estatisticas["tempo_medio_por_categoria"] = (
        df.groupby("categoria")["tempo_minutos"].mean().to_dict()
    )

    # Percentual de atendimentos rejeitados;
    estatisticas["percentual_de_atendimentos_rejeitados"] = (rejeitados / lidos) * 100

    # Categoria mais frequente;
    estatisticas["categoria_mais_frequente"] = df["categoria"].value_counts().idxmax()

    return estatisticas
