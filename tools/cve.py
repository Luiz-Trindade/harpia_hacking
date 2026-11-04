import json
import urllib.parse
import urllib.request
from langchain_core.tools import tool


@tool
def consultar_cve_servico(servico: str, versao: str = "") -> str:
    """Consulta a API pública do NVD (National Vulnerability Database) para identificar CVEs e CVSS de um serviço."""
    termo = f"{servico} {versao}".strip()
    termo_encoded = urllib.parse.quote(termo)
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={termo_encoded}&resultsPerPage=5"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HarpiaSec-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                vulnerabilidades = data.get("vulnerabilities", [])

                if not vulnerabilidades:
                    return f"Nenhuma CVE pública encontrada no NVD para '{termo}'."

                resultados = []
                for item in vulnerabilidades:
                    cve_data = item.get("cve", {})
                    cve_id = cve_data.get("id", "N/A")

                    descriptions = cve_data.get("descriptions", [])
                    desc = next(
                        (
                            d["value"]
                            for d in descriptions
                            if d.get("lang") in ["en", "pt"]
                        ),
                        "Sem descrição disponível.",
                    )

                    metrics = cve_data.get("metrics", {})
                    cvss_v31 = metrics.get(
                        "cvssMetricV31", metrics.get("cvssMetricV30", [{}])
                    )[0].get("cvssData", {})
                    severity = cvss_v31.get("baseSeverity", "DESCONHECIDO")
                    score = cvss_v31.get("baseScore", "N/A")

                    resultados.append(
                        f"• [{cve_id}] Severidade: {severity} (CVSS: {score})\n  Descrição: {desc[:200]}..."
                    )

                return f"CVEs encontradas no NVD para '{termo}':\n\n" + "\n\n".join(
                    resultados
                )

            return f"Erro na consulta NVD (Status HTTP {resp.status})."
    except Exception as e:
        return f"Erro ao consultar NVD para '{termo}': {str(e)}"
