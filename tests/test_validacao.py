"""FIC_DEV — Módulo Python para IA — Desafio 1

Equipe: Felipe Ferreira Aguiar · Líbia Canhete Alves e Cruz · Victor Griggi Moreira Regis da Silva
Turma: Noturno

Testes das regras de validação.
"""

# python -m pytest

import pytest

from src.validacao import (
    CampoObrigatorioError,
    DataInvalidaError,
    EmailInvalidoError,
    TempoInvalidoError,
    converter_data,
    converter_tempo,
    email_valido,
    validar_registro,
)

REGISTRO_OK = {
    "protocolo": "SUP-2026-0001",
    "data": "2026-07-02",
    "email": "aluno1@example.com",
    "categoria": "Ambiente Virtual",
    "status": "aberto",
    "tempo_minutos": "75",
    "descricao": " Solicitação de suporte número 1  ",
}


def test_email_valido():
    assert email_valido("aluno1@example.com")
    assert not email_valido("email-invalido")
    assert not email_valido("nome@dominio")


def test_os_quatro_formatos_de_data_viram_iso():
    assert converter_data("2026-07-02") == "2026-07-02"
    assert converter_data("02-07-2026") == "2026-07-02"
    assert converter_data("2026/07/02") == "2026-07-02"
    assert converter_data("02/07/2026") == "2026-07-02"


def test_data_que_nao_existe_no_calendario():
    with pytest.raises(DataInvalidaError):
        converter_data("31/02/2026")


def test_tempo_nao_numerico():
    with pytest.raises(TempoInvalidoError):
        converter_tempo("muito")


def test_tempo_negativo():
    with pytest.raises(TempoInvalidoError):
        converter_tempo("-15")


def test_tempo_alto_e_aceito():
    assert converter_tempo("2000") == 2000


def test_registro_valido():
    resultado = validar_registro(REGISTRO_OK)

    assert resultado["data"] == "2026-07-02"
    assert resultado["tempo_minutos"] == 75
    assert resultado["descricao"] == "Solicitação de suporte número 1"


def test_campo_obrigatorio_vazio():
    registro = dict(REGISTRO_OK, email="")

    with pytest.raises(CampoObrigatorioError) as erro:
        validar_registro(registro)

    assert "email" in str(erro.value)


def test_registro_com_email_invalido():
    registro = dict(REGISTRO_OK, email="email-invalido")

    with pytest.raises(EmailInvalidoError):
        validar_registro(registro)
