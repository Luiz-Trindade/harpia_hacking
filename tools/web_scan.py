import json
import shlex
import subprocess
from langchain_core.tools import tool


@tool
def analisar_vulnerabilidades_web(
    url_alvo: str, severidade: str = "critical,high,medium"
) -> str:
    """Executa uma varredura de vulnerabilidades web na URL especificada utilizando o scanner Nuclei.
    Identifica falhas de segurança, misconfigurations, CVEs expostas e endpoints sensíveis.

    Args:
        url_alvo: URL completa do site ou IP com porta (ex: 'https://exemplo.com' ou 'http://192.168.0.1:8080').
        severidade: Níveis de severidade separados por vírgula (ex: 'critical,high,medium' ou 'low,info').
    """
    cmd = [
        "nuclei",
        "-u",
        url_alvo,
        "-severity",
        severidade,
        "-jsonl",
        "-silent",
        "-timeout",
        "5",
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if resultado.returncode != 0 and not resultado.stdout:
            return f"Erro na execução do Nuclei: {resultado.stderr}"

        linhas = resultado.stdout.strip().split("\n")
        if not linhas or linhas == [""]:
            return f"Varredura concluída. Nenhuma vulnerabilidade de severidade [{severidade}] encontrada em {url_alvo}."

        vulnerabilidades = []
        for linha in linhas[:15]:  # Limita aos 15 achados mais relevantes
            if not linha.strip():
                continue
            data = json.loads(linha)
            template_id = data.get("template-id", "N/A")
            info = data.get("info", {})
            nome = info.get("name", template_id)
            sev = info.get("severity", "unknown").upper()
            matched = data.get("matched-at", url_alvo)
            cve_id = info.get("classification", {}).get("cve-id", [])

            detalhe = f"• [{sev}] {nome} ({template_id})\n  Endpoint afetado: {matched}"
            if cve_id:
                detalhe += f"\n  CVE: {', '.join(cve_id)}"

            vulnerabilidades.append(detalhe)

        return f"Vulnerabilidades detectadas em {url_alvo}:\n\n" + "\n\n".join(
            vulnerabilidades
        )

    except FileNotFoundError:
        return (
            "Erro: O utilitário 'nuclei' não está instalado no sistema.\n"
            "Instale-o via Go (`go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest`) "
            "ou baixe o binário em https://github.com/projectdiscovery/nuclei/releases"
        )
    except subprocess.TimeoutExpired:
        return "Erro: A varredura do Nuclei excedeu o tempo limite de 120 segundos."
    except Exception as e:
        return f"Erro ao analisar o site: {str(e)}"
