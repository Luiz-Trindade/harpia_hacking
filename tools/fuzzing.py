import json
import subprocess
import tempfile
from pathlib import Path
from langchain_core.tools import tool

# Wordlist fallback embutida para caso nenhuma wordlist customizada seja fornecida
WORDLIST_EMBUTIDA = [
    "admin",
    "administrator",
    "login",
    "wp-admin",
    "api",
    "v1",
    "v2",
    "backup",
    "backups",
    "db",
    "database",
    ".env",
    ".git",
    "config",
    "settings",
    "dashboard",
    "uploads",
    "assets",
    "test",
    "dev",
    "staging",
]


@tool
def fuzzing_diretorios(url_alvo: str, wordlist_path: str = "") -> str:
    """Executa fuzzing de diretórios e arquivos em uma aplicação web para descobrir caminhos ocultos,
    painéis administrativos, arquivos de backup (.env, .git) e rotas não catalogadas.

    Args:
        url_alvo: URL base da aplicação (ex: 'http://192.168.0.1:8080' ou 'https://exemplo.com').
        wordlist_path: Caminho opcional para arquivo de wordlist customizado (ex: '/usr/share/wordlists/dirb/common.txt').
    """
    url_limpa = url_alvo.rstrip("/")
    target_fuzz = f"{url_limpa}/FUZZ"

    temp_file = None
    if not wordlist_path or not Path(wordlist_path).exists():
        temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        temp_file.write("\n".join(WORDLIST_EMBUTIDA))
        temp_file.close()
        wordlist_exec = temp_file.name
    else:
        wordlist_exec = wordlist_path

    cmd = [
        "ffuf",
        "-u",
        target_fuzz,
        "-w",
        wordlist_exec,
        "-mc",
        "200,204,301,302,307,401,403",
        "-of",
        "json",
        "-s",
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if temp_file:
            Path(temp_file.name).unlink(missing_ok=True)

        if resultado.returncode != 0 and not resultado.stdout:
            return f"Erro na execução do ffuf: {resultado.stderr}"

        try:
            data = json.loads(resultado.stdout)
            results = data.get("results", [])
        except json.JSONDecodeError:
            return "Erro ao processar resposta JSON do ffuf."

        if not results:
            return f"Nenhum diretório ou arquivo oculto encontrado em {url_alvo}."

        achados = []
        for r in results:
            status = r.get("status", "N/A")
            length = r.get("length", "N/A")
            url_encontrada = r.get("url", "N/A")
            input_word = r.get("input", {}).get("FUZZ", "N/A")

            achados.append(
                f"• [{status}] /{input_word} (Tamanho: {length} bytes) → {url_encontrada}"
            )

        return f"Diretórios e rotas identificadas em {url_alvo}:\n\n" + "\n".join(
            achados
        )

    except FileNotFoundError:
        if temp_file:
            Path(temp_file.name).unlink(missing_ok=True)
        return (
            "Erro: O utilitário 'ffuf' não está instalado no sistema.\n"
            "Instale via terminal com: `sudo apt install ffuf`"
        )
    except subprocess.TimeoutExpired:
        if temp_file:
            Path(temp_file.name).unlink(missing_ok=True)
        return "Erro: A varredura de fuzzing excedeu o tempo limite de 60 segundos."
    except Exception as e:
        if temp_file:
            Path(temp_file.name).unlink(missing_ok=True)
        return f"Erro ao executar fuzzing de diretórios: {str(e)}"
