import logging

import pandas as pd

logger = logging.getLogger("suporte.processamento")

CATEGORIA_PADRAO = "Não classificada"


def mapear_categoria(categoria: str | None, categorias: dict) -> str:
    """Mapeia a categoria informada para a categoria padrão se não for encontrada.

    Returns:
        A categoria padrão se não for encontrada, caso contrário, a categoria original.
    """

    for padrao, alternativas in categorias.items():
        if categoria is None:
            return CATEGORIA_PADRAO
        elif categoria.lower() in alternativas:
            return padrao

    return CATEGORIA_PADRAO


def eliminar_duplicatas(validos: list[dict]) -> pd.DataFrame:
    """Mantém só a primeira ocorrência de cada protocolo."""
    df = pd.DataFrame(validos)
    duplicados = df[df.duplicated(subset="protocolo", keep="first")]
    for protocolo in duplicados["protocolo"]:
        logger.warning(
            "Protocolo '%s' duplicado; mantida a primeira ocorrência",
            protocolo,
        )
    return df.drop_duplicates(subset="protocolo", keep="first")


if __name__ == "__main__":
    print(mapear_categoria("acesso ao ambiente VIRTUAL"))
    print(mapear_categoria("CATEGORIA INVÁLIDA"))
    print(mapear_categoria(None))
