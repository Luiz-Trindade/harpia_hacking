import subprocess
from langchain_core.tools import tool


@tool
def consultar_dns_whois(dominio: str) -> str:
    """Extrai informações de WHOIS (propriedade) e registros de DNS importantes (A, MX, TXT) de um domínio."""
    resultado_final = f"🔍 OSINT para {dominio}:\n\n"

    # DNS TXT (Procura por SPF, DMARC e chaves de verificação)
    try:
        dig_txt = subprocess.run(
            ["dig", "+short", "TXT", dominio], capture_output=True, text=True
        )
        if dig_txt.stdout:
            resultado_final += "[Registros TXT (SPF/DMARC)]:\n" + dig_txt.stdout + "\n"
    except Exception:
        pass

    # DNS MX (Servidores de E-mail)
    try:
        dig_mx = subprocess.run(
            ["dig", "+short", "MX", dominio], capture_output=True, text=True
        )
        if dig_mx.stdout:
            resultado_final += "[Servidores de E-mail (MX)]:\n" + dig_mx.stdout + "\n"
    except Exception:
        pass

    # WHOIS básico
    try:
        whois_cmd = subprocess.run(
            ["whois", dominio], capture_output=True, text=True, timeout=10
        )
        whois_relevante = [
            linha
            for linha in whois_cmd.stdout.split("\n")
            if "Creation Date" in linha
            or "Registrar:" in linha
            or "Name Server" in linha
        ]
        if whois_relevante:
            resultado_final += "[WHOIS Básico]:\n" + "\n".join(
                list(set(whois_relevante))
            )
    except Exception:
        pass

    return resultado_final
