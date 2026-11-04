import subprocess
import urllib.parse
import urllib.request
from langchain_core.tools import tool


@tool
def consultar_fabricante_mac(ip_alvo: str) -> str:
    """Obtém o endereço MAC de um IP local na tabela ARP e consulta a base OUI para identificar o fabricante."""
    mac = None

    try:
        resultado = subprocess.run(
            ["ip", "neighbor", "show", ip_alvo],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if resultado.returncode == 0 and resultado.stdout:
            partes = resultado.stdout.split()
            if "lladdr" in partes:
                idx = partes.index("lladdr")
                if idx + 1 < len(partes):
                    mac = partes[idx + 1]
    except Exception:
        pass

    if not mac:
        try:
            resultado = subprocess.run(
                ["arp", "-n", ip_alvo], capture_output=True, text=True, timeout=5
            )
            if resultado.returncode == 0 and resultado.stdout:
                linhas = resultado.stdout.strip().split("\n")
                if len(linhas) > 1:
                    colunas = linhas[1].split()
                    if len(colunas) >= 3:
                        mac = colunas[2]
        except Exception:
            pass

    if not mac or mac == "<incomplete>":
        return f"Não foi possível obter o endereço MAC para {ip_alvo} na tabela ARP."

    try:
        url = f"https://api.macvendors.com/{urllib.parse.quote(mac)}"
        req = urllib.request.Request(url, headers={"User-Agent": "HarpiaSec-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                fabricante = resp.read().decode("utf-8").strip()
                return f"IP: {ip_alvo} | MAC: {mac} | Fabricante (OUI): {fabricante}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return (
                f"IP: {ip_alvo} | MAC: {mac} | Fabricante: Não encontrado na base OUI."
            )
    except Exception as e:
        return f"IP: {ip_alvo} | MAC: {mac} | Erro OUI: {str(e)}"

    return f"IP: {ip_alvo} | MAC: {mac} | Fabricante: Indeterminado."
