from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


@tool
def gerar_relatorio_pdf(
    titulo: str, conteudo: str, nome_arquivo: str = "relatorio_harpiasec.pdf"
) -> str:
    """Gera um relatório executivo em formato PDF no diretório raiz do projeto com os achados da auditoria.

    Args:
        titulo: Título principal do relatório (ex: 'Relatório de Auditoria - exemplo.com').
        conteudo: Resumo textual detalhado dos achados, vulnerabilidades e recomendações.
        nome_arquivo: Nome do arquivo PDF de saída (ex: 'auditoria_exemplo.pdf').
    """
    if not nome_arquivo.endswith(".pdf"):
        nome_arquivo += ".pdf"

    caminho_saida = Path.cwd() / nome_arquivo

    try:
        doc = SimpleDocTemplate(
            str(caminho_saida),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Estilos customizados para o documento
        style_title = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1b4332"),
            spaceAfter=6,
        )

        style_subtitle = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#555555"),
            spaceAfter=15,
        )

        style_body = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#222222"),
            spaceAfter=8,
        )

        elements = []

        # Cabeçalho
        elements.append(Paragraph("🛡️ HarpiaSec - Security Audit Report", style_title))
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        elements.append(
            Paragraph(
                f"<b>Alvo/Título:</b> {titulo} | <b>Data:</b> {data_atual}",
                style_subtitle,
            )
        )
        elements.append(
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=colors.HexColor("#2d6a4f"),
                spaceAfter=15,
            )
        )

        # Processamento do conteúdo linha por linha
        linhas = conteudo.split("\n")
        for linha in linhas:
            linha_limpa = linha.strip()
            if not linha_limpa:
                elements.append(Spacer(1, 6))
                continue

            # Formatação básica de marcação
            if linha_limpa.startswith("### "):
                p_style = ParagraphStyle(
                    "H3",
                    parent=styles["Heading3"],
                    fontSize=12,
                    textColor=colors.HexColor("#2d6a4f"),
                    spaceBefore=8,
                    spaceAfter=4,
                )
                elements.append(Paragraph(linha_limpa.replace("### ", ""), p_style))
            elif linha_limpa.startswith("## "):
                p_style = ParagraphStyle(
                    "H2",
                    parent=styles["Heading2"],
                    fontSize=14,
                    textColor=colors.HexColor("#1b4332"),
                    spaceBefore=12,
                    spaceAfter=6,
                )
                elements.append(Paragraph(linha_limpa.replace("## ", ""), p_style))
            elif linha_limpa.startswith("• ") or linha_limpa.startswith("- "):
                texto_item = linha_limpa[2:]
                elements.append(Paragraph(f"&bull; {texto_item}", style_body))
            else:
                # Converte quebras de linha simples
                elements.append(Paragraph(linha_limpa, style_body))

        # Rodapé visual
        elements.append(Spacer(1, 15))
        elements.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#cccccc"),
                spaceBefore=10,
                spaceAfter=10,
            )
        )
        elements.append(
            Paragraph(
                "<i>Relatório gerado automaticamente pelo agente HarpiaSec. Confidencial.</i>",
                style_subtitle,
            )
        )

        doc.build(elements)
        return f"✅ Relatório PDF gerado com sucesso no diretório raiz: {caminho_saida.name}"

    except Exception as e:
        return f"❌ Erro ao gerar o relatório PDF: {str(e)}"
