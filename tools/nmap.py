import shlex
import subprocess
from langchain_core.tools import tool


@tool
def executar_nmap_scan(alvo: str, opcoes: str = "-sC -sV -O -T4") -> str:
    """Executa uma varredura Nmap detalhada no alvo especificado para mapear portas,
    serviços, versões, scripts NSE padrão e sistema operacional.

    Args:
        alvo: IP ou hostname do alvo (ex: '192.168.1.1' ou 'scanme.nmap.org').
        opcoes: Flags do Nmap. O padrão '-sC -sV -O -T4' realiza varredura profunda de serviços e SO.
    """
    cmd = ["nmap"] + shlex.split(opcoes) + [alvo]

    try:
        # Aumentado o timeout para 600 segundos devido ao tempo exigido por scripts NSE e detecção de SO
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if resultado.returncode == 0:
            saida = resultado.stdout.strip()
            return (
                saida
                if saida
                else "Varredura concluída, mas nenhuma porta aberta ou resposta foi obtida."
            )
        else:
            # Caso falhe por falta de privilégios de root para a flag -O
            if "Requires root privileges" in resultado.stderr:
                return (
                    "⚠️ Erro de permissão: As opções selecionadas (ex: -O ou -sS) exigem privilégios de superusuário (root).\n"
                    "Execute a aplicação com 'sudo' ou altere as opções para '-sV -sC' (sem detecção de SO via RAW sockets)."
                )
            return f"Erro na execução do Nmap (código {resultado.returncode}):\n{resultado.stderr}"

    except FileNotFoundError:
        return "Erro: O utilitário 'nmap' não está instalado no sistema."
    except subprocess.TimeoutExpired:
        return "Erro: A varredura profunda excedeu o tempo limite de 600 segundos (10 minutos)."
    except Exception as e:
        return f"Erro ao executar o Nmap: {str(e)}"
