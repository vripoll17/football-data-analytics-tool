from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from charts import generate_radar_chart, generate_top3_players_by_action_chart, generate_tornado_chart, create_player_stats_table
from utils.data_processing import calculate_match_stats, calculate_player_stats, clean_data
from ai.analysis import generate_ai_analysis

def load_dataframes(csv_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"El archivo CSV no existe: {csv_file}")

    cleaned_df = clean_data(pd.read_csv(csv_file))
    teams_df = calculate_match_stats(cleaned_df)
    players_df = calculate_player_stats(cleaned_df)
    return teams_df, players_df


def _analysis_flowables(ai_analysis: str | None, styles: dict) -> list[Paragraph | Spacer]:
    if not ai_analysis:
        return [Paragraph("No se pudo generar el análisis de IA.", styles["BodyText"])]

    flowables: list[Paragraph | Spacer] = []
    for raw_line in ai_analysis.splitlines():
        line = raw_line.strip()
        if not line:
            flowables.append(Spacer(1, 0.15 * cm))
        elif line.startswith("### "):
            flowables.append(Paragraph(escape(line[4:]), styles["Heading3"]))
        elif line.startswith("## "):
            flowables.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            flowables.append(Paragraph(escape(line[2:]), styles["Heading1"]))
        elif line.startswith("- ") or line.startswith("* "):
            flowables.append(Paragraph(escape(line[2:]), styles["BodyText"], bulletText="-"))
        else:
            flowables.append(Paragraph(escape(line), styles["BodyText"]))

    return flowables


def build_pdf(
    tornado_path: Path,
    radar_path: Path,
    top3_path: Path,
    players_df: pd.DataFrame,
    ai_analysis: str | None,
    output_pdf: Path,
) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output_pdf), pagesize=A4, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=26, spaceAfter=30)
    note_style = ParagraphStyle("Note", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)
    story = [
        Spacer(1, 1 * cm),
        Paragraph("REPORTE VISUAL DE PARTIDO", title_style),
        Paragraph("Análisis comparativo de volumen de juego", ParagraphStyle("Sub", parent=styles["Normal"], alignment=TA_CENTER, fontSize=12, textColor=colors.grey)),
        Spacer(1, 2 * cm),
        Image(str(tornado_path), width=19 * cm, height=13 * cm),
        Spacer(1, 2 * cm),
        Paragraph("<i>* Los valores indican el número total de eventos registrados.</i>", note_style),
        PageBreak(),
        Spacer(1, 1 * cm),
        Paragraph("COMPARATIVA TELARAÑA ENTRE EQUIPOS", title_style),
        Spacer(1, 1 * cm),
        Image(str(radar_path), width=17 * cm, height=12 * cm),
        Spacer(1, 1 * cm),
        Paragraph("<i>* Escala porcentual (0 a 1) basada en las métricas definidas.</i>", note_style),
        PageBreak(),
        Paragraph("ESTADÍSTICAS POR JUGADOR", title_style),
        Spacer(1, 0.5 * cm),
    ]

    table = Table(create_player_stats_table(players_df), colWidths=[3.3 * cm, 1.3 * cm, 1.2 * cm, 1.9 * cm, 1.1 * cm, 1.8 * cm, 1.8 * cm, 1.3 * cm, 1.4 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0047AB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    story.extend([
        table,
        Spacer(1, 1 * cm),
        Paragraph("TOP 3 JUGADORES POR ACCIÓN", title_style),
        Image(str(top3_path), width=18 * cm, height=12 * cm),
        PageBreak(),
        Paragraph("ANÁLISIS GENERADO POR IA", title_style),
        Spacer(1, 0.5 * cm),
        *_analysis_flowables(ai_analysis, styles),
    ])
    document.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un informe PDF a partir de un CSV de acciones.")
    parser.add_argument("csv_file")
    args = parser.parse_args()
    csv_path = Path(args.csv_file)
    output_path = Path("reports") / f"Visual_Report_{csv_path.stem}.pdf"

    try:
        teams_df, players_df = load_dataframes(csv_path)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            tornado_path = generate_tornado_chart(teams_df, output_dir)
            radar_path = generate_radar_chart(teams_df, output_dir)
            top3_path = generate_top3_players_by_action_chart(players_df, output_dir)
            ai_analysis = generate_ai_analysis(players_df, teams_df)
            build_pdf(tornado_path, radar_path, top3_path, players_df, ai_analysis, output_path)
        print(f"Informe visual generado en: {output_path.absolute()}")
    except Exception as error:
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
