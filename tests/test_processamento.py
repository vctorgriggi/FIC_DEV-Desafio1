"""FIC_DEV — Módulo Python para IA — Desafio 1

Equipe: Felipe Ferreira Aguiar · Líbia Canhete Alves e Cruz · Victor Griggi Moreira Regis da Silva
Turma: Noturno

Testes do tratamento dos dados.
"""

# python -m pytest

import pandas as pd

from src.processamento import CATEGORIA_PADRAO, padronizar_categoria, tratar_dados

CATEGORIAS = {
    "Acesso ao AVA": ["ava", "acesso ava", "ambiente virtual"],
    "Senha": ["senha", "password"],
}

REGISTROS = [
    {
        "protocolo": "sup-2026-0001",
        "data": "2026-07-02",
        "email": "Aluno1@Example.com",
        "categoria": "  Ambiente Virtual  ",
        "status": "ABERTO",
        "tempo_minutos": 75,
        "descricao": "  primeiro atendimento  ",
    },
    {
        "protocolo": "SUP-2026-0001",  # mesmo protocolo após uniformizar -> duplicado
        "data": "2026-07-03",
        "email": "aluno2@example.com",
        "categoria": "PASSWORD",
        "status": "resolvido",
        "tempo_minutos": 40,
        "descricao": "",
    },
    {
        "protocolo": "SUP-2026-0002",
        "data": "2026-07-04",
        "email": "aluno3@example.com",
        "categoria": "categoria desconhecida",
        "status": "em andamento",
        "tempo_minutos": 10,
        "descricao": "",
    },
]


def test_padronizar_categoria_reconhece_sinonimo():
    mapa = {"senha": "Senha", "password": "Senha"}
    assert padronizar_categoria("PASSWORD", mapa) == "Senha"


def test_padronizar_categoria_sem_correspondencia():
    mapa = {"senha": "Senha"}
    assert padronizar_categoria("categoria desconhecida", mapa) == CATEGORIA_PADRAO


def test_tratar_dados_remove_duplicidade_mantendo_primeira_ocorrencia():
    df = tratar_dados(REGISTROS, CATEGORIAS)

    assert len(df) == 2
    assert df.loc[df["protocolo"] == "SUP-2026-0001", "email"].iloc[0] == "aluno1@example.com"


def test_tratar_dados_uniformiza_caixa():
    df = tratar_dados(REGISTROS, CATEGORIAS)

    assert (df["protocolo"] == df["protocolo"].str.upper()).all()
    assert (df["email"] == df["email"].str.lower()).all()
    assert (df["status"] == df["status"].str.lower()).all()


def test_tratar_dados_padroniza_categoria():
    df = tratar_dados(REGISTROS, CATEGORIAS)

    assert df.loc[df["protocolo"] == "SUP-2026-0001", "categoria"].iloc[0] == "Acesso ao AVA"
    assert df.loc[df["protocolo"] == "SUP-2026-0002", "categoria"].iloc[0] == CATEGORIA_PADRAO


def test_tratar_dados_preenche_descricao_ausente():
    df = tratar_dados(REGISTROS, CATEGORIAS)

    assert df.loc[df["protocolo"] == "SUP-2026-0002", "descricao"].iloc[0] == "Sem descrição"


def test_tratar_dados_converte_data_para_datetime():
    df = tratar_dados(REGISTROS, CATEGORIAS)

    assert pd.api.types.is_datetime64_any_dtype(df["data"])
