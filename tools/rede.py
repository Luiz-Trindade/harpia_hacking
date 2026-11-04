import subprocess
from langchain_core.tools import tool


@tool
def obter_informacoes_rede() -> str:
    """Executa o comando 'ifconfig' (ou 'ip addr' como fallback) para listar as interfaces de rede ativas."""
    try:
        resultado = subprocess.run(
            ["ifconfig"], capture_output=True, text=True, timeout=10
        )
        if resultado.returncode == 0 and resultado.stdout.strip():
            return resultado.stdout
    except FileNotFoundError:
        pass

    try:
        resultado = subprocess.run(
            ["ip", "addr"], capture_output=True, text=True, timeout=10
        )
        if resultado.returncode == 0:
            return resultado.stdout
        return f"Erro ao obter interfaces de rede: {resultado.stderr}"
    except Exception as e:
        return f"Erro ao executar comando de rede: {str(e)}"
