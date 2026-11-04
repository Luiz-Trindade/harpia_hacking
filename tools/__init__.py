from .cve import consultar_cve_servico
from .mac import consultar_fabricante_mac
from .nmap import executar_nmap_scan
from .rede import obter_informacoes_rede
from .web_scan import analisar_vulnerabilidades_web
from .fuzzing import fuzzing_diretorios

ALL_TOOLS = [
    obter_informacoes_rede,
    executar_nmap_scan,
    consultar_cve_servico,
    consultar_fabricante_mac,
    analisar_vulnerabilidades_web,
    fuzzing_diretorios,
]

__all__ = ["ALL_TOOLS"]
