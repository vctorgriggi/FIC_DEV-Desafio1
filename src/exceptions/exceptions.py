# Exceção do módulo
class ArquivoAusenteError(Exception):
    """Arquivo obrigatório não encontrado ou ilegível."""
    
# Exceções customizadas
class RegistroInvalidoError(Exception):
    """Classe base para os erros de validação de um atendimento."""


class CampoObrigatorioError(RegistroInvalidoError):
    def __init__(self, campo: str):
        self.campo = campo
        super().__init__(f"campo '{campo}' obrigatório e vazio")


class EmailInvalidoError(RegistroInvalidoError):
    def __init__(self, valor: str):
        self.valor = valor
        super().__init__(f"e-mail '{valor}' em formato inválido")


class DataInvalidaError(RegistroInvalidoError):
    def __init__(self, valor: str):
        self.valor = valor
        super().__init__(f"data '{valor}' em formato não reconhecido")


class TempoInvalidoError(RegistroInvalidoError):
    def __init__(self, valor: str): 
        self.valor = valor
        super().__init__(f"tempo '{valor}' inválido, esperado minutos > 0")
