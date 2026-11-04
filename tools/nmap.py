import shlex
import subprocess
from langchain_core.tools import tool


@tool
def executar_nmap_scan(alvo: str, opcoes: str = "-sV -F") -> str:
    """Executa uma varredura Nmap no alvo especificado para mapear portas e serviços abertos."""
    cmd = ["nmap"] + shlex.split(opcoes) + [alvo]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if resultado.returncode == 0:
            return (
                resultado.stdout
                if resultado.stdout
                else "Varredura concluída sem dados de saída."
            )
        else:
            return f"Erro na execução do Nmap (código {resultado.returncode}):\n{resultado.stderr}"
    except FileNotFoundError:
        return "Erro: O utilitário 'nmap' não está instalado no sistema."
    except subprocess.TimeoutExpired:
        return "Erro: A varredura excedeu o tempo limite de 180 segundos."
    except Exception as e:
        return f"Erro ao executar o Nmap: {str(e)}"
