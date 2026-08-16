import re
from datetime import datetime

from src.exceptions.exceptions import (
    CampoObrigatorioError,
    DataInvalidaError,
    EmailInvalidoError,
    RegistroInvalidoError,
    TempoInvalidoError,
)

# Regras de validação
# Categoria vazia não rejeita o registro: o tratamento mapeia para
# "Não classificada" quando não há correspondência em categorias.json.
CAMPOS_OBRIGATORIOS = (
    "protocolo",
    "data",
    "email",
    "status",
    "tempo_minutos",
)

PADRAO_PROTOCOLO = re.compile(r"^SUP-\d{4}-\d{4}$")
PADRAO_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-zA-Z]{2,}$")

FORMATOS_DATA = ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y")

TEMPO_MIN = 1


# Validações de campo
def protocolo_valido(protocolo: str) -> bool:
    return bool(PADRAO_PROTOCOLO.match(protocolo))


def email_valido(email: str) -> bool:
    return bool(PADRAO_EMAIL.match(email))


def converter_data(valor: str) -> str:
    """Converte a data para AAAA-MM-DD, testando as formatações conhecidas.

    Raises:
        DataInvalidaError: Se nenhuma das formatações conhecidas servir.
    """
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(valor, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise DataInvalidaError(valor)


def converter_tempo(valor: str) -> int:
    try:
        minutos = int(valor)
    except ValueError:
        raise TempoInvalidoError(valor) from None

    # Tempo alto continua sendo atendimento; só recusamos o impossível
    if minutos < TEMPO_MIN:
        raise TempoInvalidoError(valor)

    return minutos

def converter_status(status: str) -> str:
    return status.lower().strip()

# Validação do registro completo
def validar_registro(registro: dict) -> dict:
    """Valida uma linha do CSV e devolve o registro já convertido.

    Returns:
        Dicionário com os campos limpos, data em ISO e tempo como inteiro.

    Raises:
        CampoObrigatorioError: Se algum campo obrigatório estiver vazio.
        EmailInvalidoError: Se o e-mail for malformado.
        DataInvalidaError: Se a data não for reconhecida.
        TempoInvalidoError: Se o tempo não for um número positivo.
    """
    campos = {
        chave: (registro.get(chave) or "").strip() for chave in CAMPOS_OBRIGATORIOS
    }

    for chave, valor in campos.items():
        if not valor:
            raise CampoObrigatorioError(chave)

    email = campos["email"].lower()

    if not email_valido(email):
        raise EmailInvalidoError(email)

    return {
        "protocolo": campos["protocolo"].upper(),
        "data": converter_data(campos["data"]),
        "email": email,
        "categoria": (registro.get("categoria") or "").strip(),
        "status": converter_status(campos["status"]),
        "tempo_minutos": converter_tempo(campos["tempo_minutos"]),
        "descricao": (registro.get("descricao") or "").strip(),
    }


if __name__ == "__main__":
    # Teste rápido do módulo
    bom = {
        "protocolo": "SUP-2026-0001",
        "data": "02/07/2026",
        "email": "Aluno1@Example.com",
        "categoria": "Ambiente Virtual",
        "status": "aberto",
        "tempo_minutos": "75",
        "descricao": "  teste  ",
    }
    print("Válido:", validar_registro(bom))

    ruim = dict(bom, email="email-invalido")
    try:
        validar_registro(ruim)
    except RegistroInvalidoError as e:
        print("Inválido:", e)
