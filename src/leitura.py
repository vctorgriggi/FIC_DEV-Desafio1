import csv
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger("suporte.leitura")

# Padrões do arquivo de observações
# Protocolo: SUP-2026-0003, ou 2026-0042 logo depois da palavra "protocolo".
# Sem essa segunda condição, \d{4}-\d{4} "batia" com o 3333-4455 do telefone.
PADRAO_PROTOCOLO = re.compile(
    r"\bSUP-(\d{4}-\d{4})\b|\bprotocolo\s+(\d{4}-\d{4})\b",
    re.IGNORECASE,
)

# (65) 99999-1203, 65 3333-4455, 6533334455
PADRAO_TELEFONE = re.compile(r"\(?\d{2}\)?[\s.-]?9?[\s.-]?\d{4}[\s.-]?\d{4}")


# Exceção do módulo
class ArquivoAusenteError(Exception):
    """Arquivo obrigatório não encontrado ou ilegível."""


# Configuração e estrutura de pastas
def carregar_config(caminho: Path) -> dict:
    """Lê o arquivo de configuração em JSON.

    Raises:
        ArquivoAusenteError: Se o arquivo não existir ou o JSON for inválido.
    """
    try:
        with open(caminho, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise ArquivoAusenteError(f"config não encontrado: {caminho}") from None
    except json.JSONDecodeError as e:
        raise ArquivoAusenteError(f"config com JSON inválido: {e}") from None

    obrigatorias = (
        "arquivo_atendimentos",
        "arquivo_categorias",
        "arquivo_observacoes",
        "diretorio_saida",
        "separador_csv",
    )
    faltando = [chave for chave in obrigatorias if chave not in config]
    if faltando:
        raise ArquivoAusenteError(f"config sem as chaves: {', '.join(faltando)}")

    return config


def resolver_caminhos(config: dict, raiz: Path) -> dict:
    """Converte os caminhos relativos do config em Path absoluto."""
    return {
        "atendimentos": raiz / config["arquivo_atendimentos"],
        "categorias": raiz / config["arquivo_categorias"],
        "observacoes": raiz / config["arquivo_observacoes"],
        "saida": raiz / config["diretorio_saida"],
    }


def verificar_entradas(caminhos: dict) -> None:
    """Confere se os três arquivos de entrada existem antes de processar.

    Raises:
        ArquivoAusenteError: Se algum arquivo de entrada estiver faltando.
    """
    ausentes = [
        str(caminhos[nome])
        for nome in ("atendimentos", "categorias", "observacoes")
        if not caminhos[nome].is_file()
    ]
    if ausentes:
        raise ArquivoAusenteError(
            "arquivos de entrada não encontrados: " + ", ".join(ausentes)
        )

    logger.debug("Arquivos de entrada localizados")


# Leitura dos dados
def carregar_categorias(caminho: Path) -> dict:
    """Lê o mapa de categorias oficiais e seus sinônimos.

    Returns:
        Dicionário {categoria oficial: [sinônimos]}.

    Raises:
        ArquivoAusenteError: Se o arquivo não existir ou o JSON for inválido.
    """
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ArquivoAusenteError(f"categorias não encontradas: {caminho}") from None
    except json.JSONDecodeError as e:
        raise ArquivoAusenteError(f"categorias com JSON inválido: {e}") from None


def ler_atendimentos(caminho: Path, separador: str) -> list[dict]:
    """Lê o CSV de atendimentos sem interpretar o conteúdo dos campos.

    Raises:
        ArquivoAusenteError: Se o arquivo não existir ou não puder ser lido.
    """
    registros: list[dict] = []

    try:
        with open(caminho, newline="", encoding="utf-8") as f:
            leitor = csv.DictReader(f, delimiter=separador)
            for linha in leitor:
                if not any((valor or "").strip() for valor in linha.values()):
                    continue
                registros.append(linha)
    except FileNotFoundError:
        raise ArquivoAusenteError(f"CSV não encontrado: {caminho}") from None
    except UnicodeDecodeError:
        raise ArquivoAusenteError(f"CSV com encoding inesperado: {caminho}") from None

    logger.debug("%d linhas lidas de %s", len(registros), caminho.name)
    return registros


def ler_observacoes(caminho: Path) -> str:
    """Lê o arquivo de observações, devolvendo "" se não conseguir ler."""
    try:
        return caminho.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Observações não encontradas: %s", caminho)
        return ""
    except UnicodeDecodeError:
        logger.warning("Observações com encoding inesperado, tentando latin-1")
        return caminho.read_text(encoding="latin-1")


# Extração por expressão regular
def extrair_protocolos(texto: str) -> list[str]:
    """Extrai os protocolos únicos do texto, no formato SUP-AAAA-NNNN."""
    protocolos: list[str] = []

    for achado in PADRAO_PROTOCOLO.finditer(texto):
        numero = achado.group(1) or achado.group(2)
        protocolo = f"SUP-{numero}"
        if protocolo not in protocolos:
            protocolos.append(protocolo)

    return protocolos


def extrair_telefones(texto: str) -> list[str]:
    """Extrai os telefones únicos do texto, já normalizados."""
    telefones: list[str] = []

    for achado in PADRAO_TELEFONE.finditer(texto):
        telefone = normalizar_telefone(achado.group())
        if telefone not in telefones:
            telefones.append(telefone)

    return telefones


def normalizar_telefone(telefone: str) -> str:
    """Formata como (XX) XXXX-XXXX, ou devolve o original se não tiver 10/11 dígitos."""
    digitos = re.sub(r"\D", "", telefone)

    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"

    return telefone
