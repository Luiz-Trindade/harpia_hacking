import asyncio
from pathlib import Path
import httpx
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
async def fuzzing_diretorios(url_alvo: str, wordlist_path: str = "") -> str:
    """Executa fuzzing assíncrono de diretórios e arquivos em uma aplicação web utilizando HTTPX
    para descobrir caminhos ocultos, painéis administrativos, arquivos de backup (.env, .git) e rotas.

    Args:
        url_alvo: URL base da aplicação (ex: 'http://192.168.0.1:8080' ou 'https://exemplo.com').
        wordlist_path: Caminho opcional para arquivo de wordlist customizado.
    """
    url_limpa = url_alvo.rstrip("/")

    # Carrega wordlist personalizada ou usa a embutida
    words = WORDLIST_EMBUTIDA
    if wordlist_path and Path(wordlist_path).exists():
        try:
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
                if linhas:
                    words = linhas
        except Exception as e:
            return f"Erro ao ler arquivo de wordlist: {e}"

    headers = {"User-Agent": "HarpiaSec-Fuzzer/1.0"}
    status_validos = {200, 204, 301, 302, 307, 401, 403}

    # Semáforo para limitar requisições simultâneas (evita bloqueios e estouro de conexões)
    semaphore = asyncio.Semaphore(15)

    async def verificar_rota(client: httpx.AsyncClient, word: str) -> str | None:
        target_url = f"{url_limpa}/{word.lstrip('/')}"
        async with semaphore:
            try:
                response = await client.get(
                    target_url, headers=headers, follow_redirects=False
                )
                if response.status_code in status_validos:
                    tamanho = len(response.content)
                    return f"• [{response.status_code}] /{word} (Tamanho: {tamanho} bytes) → {target_url}"
            except httpx.RequestError:
                pass
        return None

    try:
        # Client HTTPX assíncrono ignorando erros de SSL autoassinado comuns em ambientes locais/desenvolvimento
        async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
            tasks = [verificar_rota(client, word) for word in words]
            resultados = await asyncio.gather(*tasks)

        achados = [r for r in resultados if r is not None]

        if not achados:
            return f"Nenhum diretório ou arquivo oculto encontrado em {url_alvo}."

        return f"Diretórios e rotas identificadas em {url_alvo}:\n\n" + "\n".join(
            achados
        )

    except Exception as e:
        return f"Erro ao executar fuzzing de diretórios com HTTPX: {str(e)}"
